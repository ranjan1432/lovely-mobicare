from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by("-created_at")


class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Product.objects.filter(is_active=True)