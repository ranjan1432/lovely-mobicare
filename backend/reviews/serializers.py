from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review

        fields = "__all__"

        read_only_fields = (
            "is_approved",
            "created_at",
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

        if len(value) > 150:
            raise serializers.ValidationError(
                "Customer name is too long."
            )

        return value

    # =====================================================
    # RATING
    # =====================================================

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )

        return value

    # =====================================================
    # REVIEW COMMENT
    # =====================================================

    def validate_comment(self, value):
        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError(
                "Please write a more detailed review."
            )

        if len(value) > 2000:
            raise serializers.ValidationError(
                "Review is too long."
            )

        return value