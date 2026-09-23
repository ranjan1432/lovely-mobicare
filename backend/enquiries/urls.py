from django.urls import path

from .views import ContactEnquiryCreateAPIView


urlpatterns = [
    path("", ContactEnquiryCreateAPIView.as_view(), name="contact-enquiry"),
]