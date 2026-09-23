from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from .models import Order, OrderItem


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "product_name",
        "price",
        "quantity",
    )

    can_delete = False

    def has_add_permission(
        self,
        request,
        obj=None,
    ):
        return False


# =========================================================
# ORDER ADMIN
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer_name",
        "phone",
        "total_amount",
        "payment_method",
        "payment_status",
        "status",
        "stock_deducted",
        "stock_restored",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "stock_deducted",
        "stock_restored",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "email",
        "phone",
        "payment_id",
        "razorpay_order_id",
    )

    readonly_fields = (
        "user",
        "customer_name",
        "email",
        "phone",
        "address",
        "city",
        "postal_code",
        "total_amount",
        "payment_method",
        "payment_id",
        "razorpay_order_id",
        "stock_deducted",
        "stock_restored",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        OrderItemInline,
    ]

    # =====================================================
    # CANCELLED ORDER CANNOT BECOME ACTIVE AGAIN
    # =====================================================

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        if change and obj.pk:
            previous_order = (
                Order.objects
                .filter(pk=obj.pk)
                .first()
            )

            if (
                previous_order
                and previous_order.status == "cancelled"
                and obj.status != "cancelled"
            ):
                raise ValidationError(
                    "A cancelled order cannot be "
                    "changed back to an active status."
                )

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    # =====================================================
    # RESTORE CANCELLED ORDER STOCK
    #
    # IMPORTANT:
    #
    # Stock is restored ONLY when:
    #
    # 1. Order is cancelled
    # 2. Stock was actually deducted
    # 3. Stock has not already been restored
    #
    # This prevents unpaid/pending Razorpay orders from
    # incorrectly increasing product stock.
    # =====================================================

    @transaction.atomic
    def restore_cancelled_order_stock(
        self,
        order_id,
    ):
        order = (
            Order.objects
            .select_for_update()
            .get(pk=order_id)
        )

        # Only cancelled orders qualify.
        if order.status != "cancelled":
            return False

        # CRITICAL:
        # If stock was never deducted, there is
        # nothing to restore.
        #
        # Example:
        # Pending/unpaid Razorpay order.
        if not order.stock_deducted:
            return False

        # Never restore stock twice.
        if order.stock_restored:
            return False

        order_items = (
            order.items
            .select_related("product")
            .all()
        )

        for item in order_items:
            # Product may have been deleted.
            # In that case there is nothing to restore
            # for that product row.
            if not item.product_id:
                continue

            product_model = (
                item.product.__class__
            )

            product_model.objects.filter(
                pk=item.product_id
            ).update(
                stock=(
                    F("stock")
                    + item.quantity
                )
            )

        # Stock restoration has now completed.
        order.stock_restored = True

        order.save(
            update_fields=[
                "stock_restored",
            ]
        )

        return True

    # =====================================================
    # AFTER ADMIN ORDER + INLINE SAVE
    #
    # After the admin saves an order, check whether
    # cancellation requires stock restoration.
    # =====================================================

    def save_related(
        self,
        request,
        form,
        formsets,
        change,
    ):
        super().save_related(
            request,
            form,
            formsets,
            change,
        )

        self.restore_cancelled_order_stock(
            form.instance.pk
        )


# =========================================================
# ORDER ITEM ADMIN
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product_name",
        "price",
        "quantity",
    )

    search_fields = (
        "product_name",
        "order__customer_name",
    )

    readonly_fields = (
        "order",
        "product",
        "product_name",
        "price",
        "quantity",
    )

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False