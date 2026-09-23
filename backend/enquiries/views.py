from rest_framework.generics import CreateAPIView
from rest_framework.throttling import ScopedRateThrottle

from .models import ContactEnquiry
from .serializers import ContactEnquirySerializer


class ContactEnquiryCreateAPIView(CreateAPIView):
    queryset = ContactEnquiry.objects.all()
    serializer_class = ContactEnquirySerializer

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact_enquiry"