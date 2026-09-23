from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from enquiries.models import ContactEnquiry


class ContactEnquiryAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("contact-enquiry")

        self.valid_data = {
    "name": "Test Customer",
    "email": "test@example.com",
    "phone": "9876543210",
    "subject": "Mobile Service Enquiry",
    "message": "I need more information about mobile service.",
}

    def test_create_contact_enquiry_successfully(self):
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
            ContactEnquiry.objects.count(),
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
            ContactEnquiry.objects.count(),
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

        self.assertEqual(
            ContactEnquiry.objects.count(),
            0,
        )

    def test_short_message_is_rejected(self):
        data = self.valid_data.copy()
        data["message"] = "Hi"

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
            ContactEnquiry.objects.count(),
            0,
        )