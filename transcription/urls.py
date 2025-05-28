from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingFileUploadView, MeetingStatusView, ProjectViewSet, MeetingViewSet
from django.conf import settings
from django.conf.urls.static import static

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'meetings', MeetingViewSet, basename='meeting')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', MeetingFileUploadView.as_view(), name='file-upload'),
    path('status/<int:file_id>/', MeetingStatusView.as_view(), name='file-status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)