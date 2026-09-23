from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        token, _ = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "message": "Account created successfully.",
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(
            request.data.get("email", "")
        ).strip().lower()

        password = str(
            request.data.get("password", "")
        )

        if not email or not password:
            return Response(
                {
                    "detail": (
                        "Email and password are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_record = User.objects.get(
                email__iexact=email
            )
        except User.DoesNotExist:
            return Response(
                {
                    "detail": "Invalid email or password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=user_record.username,
            password=password,
        )

        if user is None:
            return Response(
                {
                    "detail": "Invalid email or password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {
                    "detail": "This account is inactive."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "message": "Login successful.",
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth:
            request.auth.delete()

        return Response(
            {
                "message": "Logged out successfully."
            },
            status=status.HTTP_200_OK,
        )