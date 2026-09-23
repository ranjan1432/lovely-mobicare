from rest_framework import serializers

from .models import Service, ServiceEnquiry


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServiceEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceEnquiry

        fields = "__all__"

        read_only_fields = (
            "status",
            "created_at",
            "updated_at",
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
    # DEVICE BRAND
    # =====================================================

    def validate_device_brand(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Please enter a valid device brand."
            )

        return value

    # =====================================================
    # DEVICE MODEL
    # =====================================================

    def validate_device_model(self, value):
        value = value.strip()

        if len(value) < 1:
            raise serializers.ValidationError(
                "Please enter your device model."
            )

        return value

    # =====================================================
    # ISSUE DESCRIPTION
    # =====================================================

    def validate_issue(self, value):
        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError(
                "Please describe the device issue in more detail."
            )

        return value