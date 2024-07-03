from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_csrf_token, FileUploadViewSet, FileDeleteViewSet, FileDeleteAllViewSet

router_file = DefaultRouter()
router_file.register(r'media', FileUploadViewSet, basename='file')
router_file.register(r'media/delete', FileDeleteViewSet, basename='file-delete')
router_file.register(r'media', FileDeleteAllViewSet, basename='file-delete-all')

urlpatterns = [
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('', include(router_file.urls)),
]
