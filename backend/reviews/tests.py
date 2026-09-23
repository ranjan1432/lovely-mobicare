from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reviews.models import Review


class ReviewAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("review-list-create")

        self.valid_data = {
            "customer_name": "Test Customer",
            "rating": 5,
            "comment": "Excellent mobile service.",
        }

    def test_submit_review_successfully(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Review.objects.get()

        self.assertFalse(review.is_approved)

    def test_unapproved_review_is_not_public(self):
        Review.objects.create(
            customer_name="Hidden Customer",
            rating=5,
            comment="Waiting for admin approval.",
            is_approved=False,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 0)

    def test_approved_review_is_public(self):
        Review.objects.create(
            customer_name="Approved Customer",
            rating=5,
            comment="Excellent service.",
            is_approved=True,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

    def test_invalid_rating_is_rejected(self):
        data = self.valid_data.copy()
        data["rating"] = 6

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Review.objects.count(), 0)

    def test_short_comment_is_rejected(self):
        data = self.valid_data.copy()
        data["comment"] = "bad"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Review.objects.count(), 0)

    def test_user_cannot_self_approve_review(self):
        data = self.valid_data.copy()
        data["is_approved"] = True

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Review.objects.get()

        self.assertFalse(review.is_approved)