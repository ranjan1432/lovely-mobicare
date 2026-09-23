from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "rating",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_approved",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "comment",
    )

    list_editable = ("is_approved",)

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)

    actions = [
        "approve_reviews",
        "unapprove_reviews",
    ]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected reviews")
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)