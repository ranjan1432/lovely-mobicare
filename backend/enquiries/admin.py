from django.contrib import admin
from .models import ContactEnquiry

# Register your models here.
@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "subject",
        "is_resolved",
        "created_at",
    )

    list_filter = (
        "is_resolved",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
    )

    list_editable = ("is_resolved",)

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)