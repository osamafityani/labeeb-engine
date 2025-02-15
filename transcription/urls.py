from django.urls import path
from .views import MeetingFileUploadView, MeetingStatusView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', MeetingFileUploadView.as_view(), name='file-upload'),
    path('status/<int:file_id>/', MeetingStatusView.as_view(), name='file-status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)