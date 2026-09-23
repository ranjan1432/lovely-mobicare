from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
)
from rest_framework.throttling import ScopedRateThrottle

from .models import Service, ServiceEnquiry
from .serializers import (
    ServiceEnquirySerializer,
    ServiceSerializer,
)


class ServiceListAPIView(ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        return (
            Service.objects
            .filter(is_active=True)
            .order_by("name")
        )


class ServiceEnquiryCreateAPIView(CreateAPIView):
    queryset = ServiceEnquiry.objects.all()
    serializer_class = ServiceEnquirySerializer

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "service_enquiry"