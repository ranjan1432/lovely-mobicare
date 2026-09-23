from rest_framework import serializers

from .models import ContactEnquiry


class ContactEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEnquiry

        fields = "__all__"

        read_only_fields = (
            "is_resolved",
            "created_at",
        )

    # =====================================================
    # CUSTOMER NAME
    # =====================================================

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Please enter a valid name."
            )

        if len(value) > 150:
            raise serializers.ValidationError(
                "Name is too long."
            )

        return value

    # =====================================================
    # PHONE NUMBER
    # =====================================================

    def validate_phone(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only numbers."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Please enter a valid 10-digit phone number."
            )

        if value[0] not in {"6", "7", "8", "9"}:
            raise serializers.ValidationError(
                "Please enter a valid Indian mobile number."
            )

        return value

    # =====================================================
    # MESSAGE
    # =====================================================

    def validate_message(self, value):
        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError(
                "Please enter a more detailed message."
            )

        return value