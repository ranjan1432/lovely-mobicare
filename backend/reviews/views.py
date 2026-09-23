from rest_framework.generics import ListCreateAPIView
from rest_framework.throttling import ScopedRateThrottle

from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateAPIView(ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return (
            Review.objects
            .filter(is_approved=True)
            .order_by("-created_at")
        )

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_scope = "review_submit"

            return [
                ScopedRateThrottle()
            ]

        return []