from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/accounts/", include("api.urls.account_urls")
    ),  # Account-related endpoints
    path("api/user/", include("api.urls.user_urls")),  # User-related endpoints
    path("api/", include("api.urls")),  # General API endpoints
]
