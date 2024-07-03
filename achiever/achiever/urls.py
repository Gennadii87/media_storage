from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/v1/", include("main.urls")),  # Основная логика

    path(
        "swagger-ui/",  # Application programing interface
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
