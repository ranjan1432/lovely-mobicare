from django.urls import path

from .views import ServiceEnquiryCreateAPIView, ServiceListAPIView


urlpatterns = [
    path("", ServiceListAPIView.as_view(), name="service-list"),
    path(
        "enquiries/",
        ServiceEnquiryCreateAPIView.as_view(),
        name="service-enquiry-create",
    ),
]