from django.urls import path

from .views import ProductDetailAPIView, ProductListAPIView


urlpatterns = [
    path("", ProductListAPIView.as_view(), name="product-list"),
    path("<int:id>/", ProductDetailAPIView.as_view(), name="product-detail"),
]