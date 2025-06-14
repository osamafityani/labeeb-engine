from django.urls import path
from . import views

urlpatterns = [
    path('auth-url/', views.get_auth_url, name='get_auth_url'),
    path('callback/', views.handle_callback, name='handle_callback'),
    path('meetings/', views.get_upcoming_meetings, name='get_upcoming_meetings'),
]