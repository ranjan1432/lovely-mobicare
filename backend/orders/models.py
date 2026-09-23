from django.conf import settings
from django.db import models

from products.models import Product


# =========================================================
# ORDER MODEL
# =========================================================

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
    ]

    PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ("refund_pending", "Refund Pending"),
    ("refunded", "Refunded"),
]

    # -----------------------------------------------------
    # Logged-in user
    # -----------------------------------------------------

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    # -----------------------------------------------------
    # Customer details
    # -----------------------------------------------------

    customer_name = models.CharField(
        max_length=150,
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20,
    )

    # -----------------------------------------------------
    # Delivery details
    # -----------------------------------------------------

    address = models.TextField()

    city = models.CharField(
        max_length=100,
    )

    postal_code = models.CharField(
        max_length=20,
    )

    # -----------------------------------------------------
    # Order status / stock state
    # -----------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # True only after this order has actually reduced
    # product stock.
    #
    # COD:
    #   True after order creation successfully deducts stock.
    #
    # Online:
    #   False while payment is pending.
    #   True only after verified payment deducts stock.
    stock_deducted = models.BooleanField(
        default=False,
    )

    # Prevent cancelled order stock from being restored
    # more than once.
    stock_restored = models.BooleanField(
        default=False,
    )

    # -----------------------------------------------------
    # Order total
    # -----------------------------------------------------

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    # -----------------------------------------------------
    # Payment
    # -----------------------------------------------------

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cod",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    # Razorpay order created before payment.
    razorpay_order_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=True,
    )

    # Razorpay payment ID after successful payment.
    payment_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    # -----------------------------------------------------
    # Dates
    # -----------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.id} - "
            f"{self.customer_name}"
        )


# =========================================================
# ORDER ITEM MODEL
# =========================================================

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Product name and price are stored at order time.
    # So old orders still keep their original details.
    product_name = models.CharField(
        max_length=200,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    def __str__(self):
        return (
            f"{self.product_name} x "
            f"{self.quantity}"
        )