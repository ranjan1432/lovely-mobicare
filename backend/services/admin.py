from django.contrib import admin
from .models import Service, ServiceEnquiry

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "starting_price",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "description",
    )

    list_editable = (
        "starting_price",
        "is_active",
    )

    ordering = ("name",)


@admin.register(ServiceEnquiry)
class ServiceEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "phone",
        "device_brand",
        "device_model",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "device_brand",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "phone",
        "email",
        "device_brand",
        "device_model",
        "issue",
    )

    list_editable = ("status",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)