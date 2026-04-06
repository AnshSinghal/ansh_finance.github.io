from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/users/", include("users.user_urls")),
    path("api/v1/records/", include("finance.record_urls")),
    path("api/v1/dashboard/", include("finance.dashboard_urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
