from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from services.models import ServiceEnquiry


class ServiceEnquiryAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("service-enquiry-create")

        self.valid_data = {
            "customer_name": "Test Customer",
            "email": "test@example.com",
            "phone": "9876543210",
            "device_brand": "Samsung",
            "device_model": "Galaxy A54",
            "issue": "Display is not working properly.",
        }

    def test_create_service_enquiry_successfully(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            ServiceEnquiry.objects.count(),
            1,
        )

    def test_invalid_phone_is_rejected(self):
        data = self.valid_data.copy()
        data["phone"] = "12345"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            ServiceEnquiry.objects.count(),
            0,
        )

    def test_invalid_email_is_rejected(self):
        data = self.valid_data.copy()
        data["email"] = "invalid-email"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_short_issue_is_rejected(self):
        data = self.valid_data.copy()
        data["issue"] = "bad"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            ServiceEnquiry.objects.count(),
            0,
        )