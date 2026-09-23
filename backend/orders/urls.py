from django.urls import path

from .views import (
    MyOrdersAPIView,
    OrderCreateAPIView,
    OrderTrackingAPIView,
    RazorpayCreateOrderAPIView,
    RazorpayVerifyPaymentAPIView,
)


urlpatterns = [
    # =====================================================
    # CREATE COD ORDER
    # POST /api/orders/
    # =====================================================
    path(
        "",
        OrderCreateAPIView.as_view(),
        name="order-create",
    ),

    # =====================================================
    # LOGGED-IN USER'S ORDERS
    # GET /api/orders/my-orders/
    # =====================================================
    path(
        "my-orders/",
        MyOrdersAPIView.as_view(),
        name="my-orders",
    ),

    # =====================================================
    # PUBLIC ORDER TRACKING
    # POST /api/orders/track/
    # =====================================================
    path(
        "track/",
        OrderTrackingAPIView.as_view(),
        name="order-track",
    ),

    # =====================================================
    # RAZORPAY - CREATE PAYMENT ORDER
    # POST /api/orders/razorpay/create/
    # =====================================================
    path(
        "razorpay/create/",
        RazorpayCreateOrderAPIView.as_view(),
        name="razorpay-create-order",
    ),

    # =====================================================
    # RAZORPAY - VERIFY PAYMENT
    # POST /api/orders/razorpay/verify/
    # =====================================================
    path(
        "razorpay/verify/",
        RazorpayVerifyPaymentAPIView.as_view(),
        name="razorpay-verify-payment",
    ),
]