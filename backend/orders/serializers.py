from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product
from .models import Order, OrderItem


# =========================================================
# ORDER ITEM SERIALIZER
# Used while creating a COD order
# =========================================================

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product_id",
            "product_name",
            "price",
            "quantity",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "price",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )

        return value


# =========================================================
# COD ORDER CREATE SERIALIZER
#
# IMPORTANT:
# /api/orders/ is kept for COD orders only.
#
# Online payments must use the separate Razorpay flow.
# =========================================================

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "customer_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "status",
            "total_amount",
            "payment_method",
            "payment_status",
            "payment_id",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "total_amount",
            "payment_status",
            "payment_id",
            "created_at",
            "updated_at",
        ]

    # =====================================================
    # CUSTOMER NAME
    # =====================================================

    def validate_customer_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Please enter a valid customer name."
            )

        if len(value) > 150:
            raise serializers.ValidationError(
                "Customer name is too long."
            )

        return value

    # =====================================================
    # PHONE
    # =====================================================

    def validate_phone(self, value):
        value = value.strip()

        if (
            not value.isdigit()
            or len(value) != 10
            or value[0] not in {"6", "7", "8", "9"}
        ):
            raise serializers.ValidationError(
                "Please enter a valid "
                "10-digit Indian mobile number."
            )

        return value

    # =====================================================
    # PIN CODE
    # =====================================================

    def validate_postal_code(self, value):
        value = value.strip()

        if (
            not value.isdigit()
            or len(value) != 6
        ):
            raise serializers.ValidationError(
                "Please enter a valid 6-digit PIN code."
            )

        return value

    # =====================================================
    # ADDRESS
    # =====================================================

    def validate_address(self, value):
        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "Please enter a complete delivery address."
            )

        return value

    # =====================================================
    # ITEMS
    # =====================================================

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one order item is required."
            )

        return items

    # =====================================================
    # OBJECT-LEVEL VALIDATION
    #
    # This endpoint is intentionally COD only.
    # COD is restricted to supported cities.
    # =====================================================

    def validate(self, attrs):
        payment_method = attrs.get(
            "payment_method",
            "cod",
        )

        if payment_method != "cod":
            raise serializers.ValidationError(
                {
                    "payment_method": (
                        "Online payments must use "
                        "the Razorpay payment option."
                    )
                }
            )

        city = attrs.get(
            "city",
            "",
        ).strip()

        normalized_city = city.lower()

        allowed_cities = {
            "erode",
            "sathy",
            "sathyamangalam",
            "gobi",
            "gobichettipalayam",
        }

        if normalized_city not in allowed_cities:
            raise serializers.ValidationError(
                {
                    "city": (
                        "Cash on Delivery is available only "
                        "in Erode, Sathyamangalam, and "
                        "Gobichettipalayam."
                    )
                }
            )

        attrs["city"] = city

        return attrs

    # =====================================================
    # SECURE COD ORDER CREATION
    #
    # - Frontend price is never trusted
    # - Frontend total is never trusted
    # - Database price is used
    # - Duplicate products are combined
    # - Product rows are locked
    # - Stock is checked
    # - Stock is reduced atomically
    # - stock_deducted is recorded
    # =====================================================

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop(
            "items"
        )

        # Combine duplicate product IDs.
        product_quantities = {}

        for item_data in items_data:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]

            product_quantities[product_id] = (
                product_quantities.get(
                    product_id,
                    0,
                )
                + quantity
            )

        secured_items = []
        total_amount = Decimal("0.00")

        for product_id, quantity in (
            product_quantities.items()
        ):
            try:
                product = (
                    Product.objects
                    .select_for_update()
                    .get(
                        id=product_id,
                        is_active=True,
                    )
                )

            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "items": (
                            f"Product with ID "
                            f"{product_id} "
                            "is not available."
                        )
                    }
                )

            if product.stock < quantity:
                raise serializers.ValidationError(
                    {
                        "items": (
                            f"Only {product.stock} "
                            f"unit(s) of {product.name} "
                            "are available."
                        )
                    }
                )

            total_amount += (
                product.price * quantity
            )

            secured_items.append(
                {
                    "product": product,
                    "product_name": product.name,
                    "price": product.price,
                    "quantity": quantity,
                }
            )

            # COD stock is deducted immediately.
            product.stock -= quantity

            product.save(
                update_fields=["stock"]
            )

        # Force COD values on the backend.
        validated_data["payment_method"] = "cod"
        validated_data["payment_status"] = "pending"

        # Stock has already been deducted above.
        # This flag lets cancellation safely know
        # whether stock should be restored.
        validated_data["stock_deducted"] = True
        validated_data["stock_restored"] = False

        order = Order.objects.create(
            total_amount=total_amount,
            **validated_data,
        )

        for item_data in secured_items:
            OrderItem.objects.create(
                order=order,
                **item_data,
            )

        return order


# =========================================================
# RAZORPAY CART ITEM
# =========================================================

class RazorpayPaymentItemSerializer(
    serializers.Serializer
):
    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1,
    )


# =========================================================
# RAZORPAY PAYMENT ORDER SERIALIZER
#
# This validates the customer's online-payment cart.
#
# IMPORTANT:
# - Frontend amount is never accepted
# - Frontend product price is never accepted
# - Database prices are used
# - Stock is checked
# - Stock is NOT reduced here
# - stock_deducted therefore remains False
# =========================================================

class RazorpayPaymentOrderSerializer(
    serializers.Serializer
):
    customer_name = serializers.CharField(
        max_length=150,
    )

    email = serializers.EmailField()

    phone = serializers.CharField(
        max_length=20,
    )

    address = serializers.CharField()

    city = serializers.CharField(
        max_length=100,
    )

    postal_code = serializers.CharField(
        max_length=20,
    )

    items = RazorpayPaymentItemSerializer(
        many=True,
    )

    # =====================================================
    # CUSTOMER NAME
    # =====================================================

    def validate_customer_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Please enter a valid customer name."
            )

        return value

    # =====================================================
    # PHONE
    # =====================================================

    def validate_phone(self, value):
        value = value.strip()

        if (
            not value.isdigit()
            or len(value) != 10
            or value[0] not in {"6", "7", "8", "9"}
        ):
            raise serializers.ValidationError(
                "Please enter a valid "
                "10-digit Indian mobile number."
            )

        return value

    # =====================================================
    # PIN CODE
    # =====================================================

    def validate_postal_code(self, value):
        value = value.strip()

        if (
            not value.isdigit()
            or len(value) != 6
        ):
            raise serializers.ValidationError(
                "Please enter a valid "
                "6-digit PIN code."
            )

        return value

    # =====================================================
    # ADDRESS
    # =====================================================

    def validate_address(self, value):
        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "Please enter a complete "
                "delivery address."
            )

        return value

    # =====================================================
    # CITY
    #
    # Online payment is not restricted by the COD-only
    # city rule.
    # =====================================================

    def validate_city(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Please enter a valid city."
            )

        return value

    # =====================================================
    # ITEMS
    # =====================================================

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one order item is required."
            )

        product_quantities = {}

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product_quantities[product_id] = (
                product_quantities.get(
                    product_id,
                    0,
                )
                + quantity
            )

        products = Product.objects.filter(
            id__in=product_quantities.keys(),
            is_active=True,
        )

        products_by_id = {
            product.id: product
            for product in products
        }

        for product_id, quantity in (
            product_quantities.items()
        ):
            product = products_by_id.get(
                product_id
            )

            if product is None:
                raise serializers.ValidationError(
                    (
                        f"Product with ID "
                        f"{product_id} "
                        "is not available."
                    )
                )

            if product.stock < quantity:
                raise serializers.ValidationError(
                    (
                        f"Only {product.stock} "
                        f"unit(s) of {product.name} "
                        "are available."
                    )
                )

        return items

    # =====================================================
    # NORMALIZED / SECURED CART
    #
    # Duplicate product IDs are combined.
    # Product details always come from database.
    # =====================================================

    def get_secured_items(self):
        items = self.validated_data["items"]

        product_quantities = {}

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product_quantities[product_id] = (
                product_quantities.get(
                    product_id,
                    0,
                )
                + quantity
            )

        products = Product.objects.filter(
            id__in=product_quantities.keys(),
            is_active=True,
        )

        products_by_id = {
            product.id: product
            for product in products
        }

        secured_items = []

        for product_id, quantity in (
            product_quantities.items()
        ):
            product = products_by_id[
                product_id
            ]

            secured_items.append(
                {
                    "product": product,
                    "product_name": product.name,
                    "price": product.price,
                    "quantity": quantity,
                }
            )

        return secured_items

    # =====================================================
    # BACKEND-CALCULATED TOTAL
    # =====================================================

    def calculate_total(self):
        secured_items = (
            self.get_secured_items()
        )

        total_amount = Decimal("0.00")

        for item in secured_items:
            total_amount += (
                item["price"]
                * item["quantity"]
            )

        return total_amount


# =========================================================
# ORDER TRACKING ITEM
# =========================================================

class OrderTrackingItemSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product_name",
            "price",
            "quantity",
        ]

        read_only_fields = fields


# =========================================================
# MY ORDERS / ORDER TRACKING
# =========================================================

class OrderTrackingSerializer(
    serializers.ModelSerializer
):
    items = OrderTrackingItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "customer_name",
            "status",
            "total_amount",
            "payment_method",
            "payment_status",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields