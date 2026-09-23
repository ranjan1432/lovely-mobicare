from decimal import Decimal

import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from products.models import Product

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderTrackingSerializer,
    RazorpayPaymentOrderSerializer,
)


# =========================================================
# CREATE COD ORDER
# Login is compulsory
#
# POST /api/orders/
# =========================================================

class OrderCreateAPIView(CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


# =========================================================
# LOGGED-IN USER'S ORDERS
#
# GET /api/orders/my-orders/
# =========================================================

class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )

        serializer = OrderTrackingSerializer(
            orders,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# PUBLIC ORDER TRACKING
#
# POST /api/orders/track/
# =========================================================

class OrderTrackingAPIView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "order_tracking"

    def post(self, request):
        order_id = request.data.get(
            "order_id"
        )

        phone = str(
            request.data.get(
                "phone",
                "",
            )
        ).strip()

        if not order_id or not phone:
            return Response(
                {
                    "detail": (
                        "Order ID and phone number "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order_id = int(order_id)

            if order_id < 1:
                raise ValueError

        except (TypeError, ValueError):
            return Response(
                {
                    "detail": (
                        "Please enter a valid "
                        "Order ID."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not phone.isdigit()
            or len(phone) != 10
            or phone[0] not in {"6", "7", "8", "9"}
        ):
            return Response(
                {
                    "detail": (
                        "Please enter a valid "
                        "10-digit Indian mobile number."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = (
                Order.objects
                .prefetch_related("items")
                .get(
                    id=order_id,
                    phone=phone,
                )
            )

        except Order.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Order not found. Please check "
                        "your Order ID and phone number."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderTrackingSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# RAZORPAY - CREATE PAYMENT ORDER
#
# POST /api/orders/razorpay/create/
#
# SECURITY:
# - Login required
# - Frontend price is NOT trusted
# - Frontend total is NOT trusted
# - Product price comes from database
# - Stock availability is checked
# - Local pending order is created
# - Order items are stored server-side
# - Stock is NOT deducted yet
# - stock_deducted remains False
# =========================================================

class RazorpayCreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RazorpayPaymentOrderSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        total_amount = (
            serializer.calculate_total()
        )

        secured_items = (
            serializer.get_secured_items()
        )

        if total_amount <= Decimal("0.00"):
            return Response(
                {
                    "detail": (
                        "Invalid payment amount."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount_in_paise = int(
            total_amount * 100
        )

        try:
            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET,
                )
            )

            razorpay_order = client.order.create(
                {
                    "amount": amount_in_paise,
                    "currency": "INR",
                    "payment_capture": 1,
                }
            )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Unable to start online payment. "
                        "Please try again."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        razorpay_order_id = (
            razorpay_order.get("id")
        )

        if not razorpay_order_id:
            return Response(
                {
                    "detail": (
                        "Unable to start online payment. "
                        "Please try again."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        validated_data = serializer.validated_data

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    customer_name=(
                        validated_data[
                            "customer_name"
                        ]
                    ),
                    email=validated_data[
                        "email"
                    ],
                    phone=validated_data[
                        "phone"
                    ],
                    address=validated_data[
                        "address"
                    ],
                    city=validated_data[
                        "city"
                    ],
                    postal_code=(
                        validated_data[
                            "postal_code"
                        ]
                    ),
                    status="pending",
                    total_amount=total_amount,
                    payment_method="online",
                    payment_status="pending",

                    # No stock has been deducted yet.
                    stock_deducted=False,
                    stock_restored=False,

                    razorpay_order_id=(
                        razorpay_order_id
                    ),
                )

                for item in secured_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        product_name=(
                            item["product_name"]
                        ),
                        price=item["price"],
                        quantity=item["quantity"],
                    )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Payment order was created, "
                        "but the local order could not "
                        "be prepared. Please try again."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        return Response(
            {
                "order_id": order.id,
                "razorpay_order_id": (
                    razorpay_order_id
                ),
                "razorpay_key_id": (
                    settings.RAZORPAY_KEY_ID
                ),
                "amount": amount_in_paise,
                "currency": "INR",
                "total_amount": str(
                    total_amount
                ),
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# RAZORPAY - VERIFY PAYMENT
#
# POST /api/orders/razorpay/verify/
#
# SECURITY:
# - Login required
# - Signature verified
# - Payment fetched directly from Razorpay
# - Order ID cross-checked
# - Amount cross-checked
# - Currency must be INR
# - Payment must be captured
# - Order must belong to logged-in user
# - Duplicate processing prevented
# - Product rows locked
# - Stock re-checked
# - Stock deducted only after verified payment
# =========================================================

class RazorpayVerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = str(
            request.data.get(
                "razorpay_order_id",
                "",
            )
        ).strip()

        razorpay_payment_id = str(
            request.data.get(
                "razorpay_payment_id",
                "",
            )
        ).strip()

        razorpay_signature = str(
            request.data.get(
                "razorpay_signature",
                "",
            )
        ).strip()

        if (
            not razorpay_order_id
            or not razorpay_payment_id
            or not razorpay_signature
        ):
            return Response(
                {
                    "detail": (
                        "Payment verification details "
                        "are incomplete."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = (
                Order.objects
                .prefetch_related("items")
                .get(
                    user=request.user,
                    razorpay_order_id=(
                        razorpay_order_id
                    ),
                    payment_method="online",
                )
            )

        except Order.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Payment order was not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -------------------------------------------------
        # Idempotency
        # -------------------------------------------------

        if order.payment_status == "paid":
            if (
                order.payment_id
                == razorpay_payment_id
            ):
                return Response(
                    {
                        "detail": (
                            "Payment is already verified."
                        ),
                        "order_id": order.id,
                        "payment_status": (
                            order.payment_status
                        ),
                        "status": order.status,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "detail": (
                        "This order has already been "
                        "paid using another payment."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        # -------------------------------------------------
        # Razorpay client
        # -------------------------------------------------

        try:
            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET,
                )
            )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Payment verification service "
                        "is currently unavailable."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        # -------------------------------------------------
        # Verify signature
        # -------------------------------------------------

        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": (
                        razorpay_order_id
                    ),
                    "razorpay_payment_id": (
                        razorpay_payment_id
                    ),
                    "razorpay_signature": (
                        razorpay_signature
                    ),
                }
            )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Payment verification failed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Fetch payment directly from Razorpay
        # -------------------------------------------------

        try:
            razorpay_payment = (
                client.payment.fetch(
                    razorpay_payment_id
                )
            )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Unable to confirm payment "
                        "details with Razorpay. "
                        "Please try again."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        if not isinstance(
            razorpay_payment,
            dict,
        ):
            return Response(
                {
                    "detail": (
                        "Invalid payment information "
                        "received from Razorpay."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        # -------------------------------------------------
        # Validate fetched payment
        # -------------------------------------------------

        expected_amount = int(
            order.total_amount * 100
        )

        payment_order_id = str(
            razorpay_payment.get(
                "order_id",
                "",
            )
        ).strip()

        payment_amount = (
            razorpay_payment.get(
                "amount"
            )
        )

        payment_currency = str(
            razorpay_payment.get(
                "currency",
                "",
            )
        ).strip().upper()

        payment_status = str(
            razorpay_payment.get(
                "status",
                "",
            )
        ).strip().lower()

        payment_captured = (
            razorpay_payment.get(
                "captured"
            )
        )

        if (
            payment_order_id
            != razorpay_order_id
        ):
            return Response(
                {
                    "detail": (
                        "Payment does not belong "
                        "to this order."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            payment_amount
            != expected_amount
        ):
            return Response(
                {
                    "detail": (
                        "Payment amount does not "
                        "match the order total."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment_currency != "INR":
            return Response(
                {
                    "detail": (
                        "Invalid payment currency."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            payment_status != "captured"
            or payment_captured is not True
        ):
            return Response(
                {
                    "detail": (
                        "Payment has not been "
                        "captured successfully."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        # -------------------------------------------------
        # Razorpay payment is verified.
        #
        # Lock order/products, re-check stock and deduct.
        # -------------------------------------------------

        try:
            with transaction.atomic():
                locked_order = (
                    Order.objects
                    .select_for_update()
                    .get(
                        id=order.id,
                        user=request.user,
                        payment_method="online",
                    )
                )

                # -----------------------------------------
                # Concurrent/idempotent verification
                # -----------------------------------------

                if (
                    locked_order.payment_status
                    == "paid"
                ):
                    if (
                        locked_order.payment_id
                        == razorpay_payment_id
                    ):
                        return Response(
                            {
                                "detail": (
                                    "Payment is already "
                                    "verified."
                                ),
                                "order_id": (
                                    locked_order.id
                                ),
                                "payment_status": (
                                    locked_order
                                    .payment_status
                                ),
                                "status": (
                                    locked_order.status
                                ),
                            },
                            status=(
                                status.HTTP_200_OK
                            ),
                        )

                    return Response(
                        {
                            "detail": (
                                "This order has already "
                                "been paid."
                            )
                        },
                        status=(
                            status.HTTP_409_CONFLICT
                        ),
                    )

                order_items = list(
                    locked_order
                    .items
                    .select_related("product")
                    .all()
                )

                if not order_items:
                    raise ValueError(
                        "This order does not contain "
                        "any products."
                    )

                locked_products = {}

                # -----------------------------------------
                # Lock product rows
                # -----------------------------------------

                for item in order_items:
                    if item.product_id is None:
                        raise ValueError(
                            "A product in this order "
                            "is no longer available."
                        )

                    if (
                        item.product_id
                        not in locked_products
                    ):
                        try:
                            product = (
                                Product.objects
                                .select_for_update()
                                .get(
                                    id=item.product_id,
                                    is_active=True,
                                )
                            )

                        except Product.DoesNotExist:
                            raise ValueError(
                                (
                                    f"{item.product_name} "
                                    "is no longer "
                                    "available."
                                )
                            )

                        locked_products[
                            item.product_id
                        ] = product

                # -----------------------------------------
                # Check ALL stock before reducing any
                # -----------------------------------------

                for item in order_items:
                    product = locked_products[
                        item.product_id
                    ]

                    if product.stock < item.quantity:
                        raise ValueError(
                            (
                                f"Only {product.stock} "
                                f"unit(s) of "
                                f"{item.product_name} "
                                "are currently "
                                "available."
                            )
                        )

                # -----------------------------------------
                # Reduce stock
                # -----------------------------------------

                for item in order_items:
                    product = locked_products[
                        item.product_id
                    ]

                    product.stock -= (
                        item.quantity
                    )

                    product.save(
                        update_fields=["stock"]
                    )

                # -----------------------------------------
                # Payment is successful and stock has now
                # ACTUALLY been deducted.
                # -----------------------------------------

                locked_order.payment_id = (
                    razorpay_payment_id
                )

                locked_order.payment_status = (
                    "paid"
                )

                locked_order.status = (
                    "confirmed"
                )

                # IMPORTANT:
                # Stock was successfully deducted above.
                locked_order.stock_deducted = True

                # Stock has not been restored.
                locked_order.stock_restored = False

                locked_order.save(
                    update_fields=[
                        "payment_id",
                        "payment_status",
                        "status",
                        "stock_deducted",
                        "stock_restored",
                        "updated_at",
                    ]
                )

        except ValueError as exc:
            # -------------------------------------------------
            # Razorpay payment is already verified/captured,
            # but stock became unavailable before the local
            # order could be finalized.
            #
            # The failed stock transaction above has already
            # rolled back, so no product stock was deducted.
            #
            # Persist a refund-required state in a NEW
            # transaction so admin/support can identify this
            # order later.
            # -------------------------------------------------

            try:
                with transaction.atomic():
                    refund_order = (
                        Order.objects
                        .select_for_update()
                        .get(
                            id=order.id,
                            user=request.user,
                            payment_method="online",
                        )
                    )

                    # Do not overwrite an order that another
                    # concurrent request successfully completed.
                    if refund_order.payment_status != "paid":
                        refund_order.payment_id = (
                            razorpay_payment_id
                        )

                        refund_order.payment_status = (
                            "refund_pending"
                        )

                        refund_order.stock_deducted = False
                        refund_order.stock_restored = False

                        refund_order.save(
                            update_fields=[
                                "payment_id",
                                "payment_status",
                                "stock_deducted",
                                "stock_restored",
                                "updated_at",
                            ]
                        )

            except Exception:
                # Payment has already been confirmed as captured.
                # If even the refund state cannot be persisted,
                # this requires manual review.
                return Response(
                    {
                        "detail": (
                            "Payment was received, but the "
                            "order could not be prepared and "
                            "the refund state could not be "
                            "saved. Please contact support."
                        ),
                        "payment_received": True,
                        "requires_review": True,
                        "order_id": order.id,
                    },
                    status=(
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                    ),
                )

            return Response(
                {
                    "detail": str(exc),
                    "payment_received": True,
                    "requires_refund": True,
                    "payment_status": "refund_pending",
                    "order_id": order.id,
                },
                status=status.HTTP_409_CONFLICT,
            )

        except Exception:
            # Payment was verified as captured, but local
            # finalization failed. Transaction rollback
            # prevents partial stock changes.
            return Response(
                {
                    "detail": (
                        "Payment was verified, but the "
                        "order could not be finalized. "
                        "Please contact support."
                    ),
                    "payment_received": True,
                    "requires_review": True,
                    "order_id": order.id,
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        return Response(
            {
                "detail": (
                    "Payment verified successfully."
                ),
                "order_id": locked_order.id,
                "payment_id": (
                    locked_order.payment_id
                ),
                "payment_status": (
                    locked_order.payment_status
                ),
                "status": locked_order.status,
                "total_amount": str(
                    locked_order.total_amount
                ),
            },
            status=status.HTTP_200_OK,
        )