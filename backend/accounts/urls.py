from django.urls import path

from .views import (
    CurrentUserAPIView,
    LoginAPIView,
    LogoutAPIView,
    RegisterAPIView,
)


urlpatterns = [
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="account-register",
    ),
    path(
        "login/",
        LoginAPIView.as_view(),
        name="account-login",
    ),
    path(
        "me/",
        CurrentUserAPIView.as_view(),
        name="account-me",
    ),
    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="account-logout",
    ),
]