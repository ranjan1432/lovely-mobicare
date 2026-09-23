from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def api_status(request):
    return JsonResponse(
        {
            "status": "success",
            "message": "Lovely Mobi Care API is running",
        }
    )


admin.site.site_header = "Lovely Mobi Care Administration"
admin.site.site_title = "Lovely Mobi Care Admin"
admin.site.index_title = "Store Management Dashboard"


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", api_status, name="api-status"),

    path(
        "api/products/",
        include("products.urls"),
    ),
    path(
        "api/services/",
        include("services.urls"),
    ),
    path(
        "api/reviews/",
        include("reviews.urls"),
    ),
    path(
        "api/contact/",
        include("enquiries.urls"),
    ),
    path(
        "api/orders/",
        include("orders.urls"),
    ),

    # Customer authentication
    path(
        "api/accounts/",
        include("accounts.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )