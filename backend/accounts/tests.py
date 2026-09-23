from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status


class AccountAPITests(APITestCase):

    def setUp(self):
        self.register_url = "/api/accounts/register/"
        self.login_url = "/api/accounts/login/"
        self.me_url = "/api/accounts/me/"
        self.logout_url = "/api/accounts/logout/"

        self.user_data = {
            "first_name": "Test",
            "last_name": "Customer",
            "email": "customer@example.com",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
        }

    def test_register_successfully(self):
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

        user = User.objects.get(
            email="customer@example.com"
        )

        self.assertEqual(
            user.username,
            "customer@example.com",
        )

        self.assertTrue(
            user.check_password("StrongPass123!")
        )

        self.assertNotEqual(
            user.password,
            "StrongPass123!",
        )

    def test_duplicate_email_is_rejected(self):
        self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_mismatch_is_rejected(self):
        data = self.user_data.copy()
        data["confirm_password"] = "DifferentPass123!"

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_successfully(self):
        user = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="StrongPass123!",
            first_name="Test",
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "customer@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("token", response.data)
        self.assertEqual(
            response.data["user"]["id"],
            user.id,
        )

    def test_wrong_password_is_rejected(self):
        User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "customer@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_me_requires_authentication(self):
        response = self.client.get(
            self.me_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_authenticated_user_can_access_me(self):
        user = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="StrongPass123!",
            first_name="Test",
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            "customer@example.com",
        )

    def test_logout_deletes_token(self):
        user = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="StrongPass123!",
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.post(
            self.logout_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            Token.objects.filter(user=user).exists()
        )