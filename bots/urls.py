from django.urls import path
from .views import RecordMeetingView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('record/', RecordMeetingView.as_view(), name='record-meeting'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)