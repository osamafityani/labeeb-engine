from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('transcription.urls')),
    path('bots/', include('bots.urls')),
    path('interface/', include('interface.urls')),
    path('auth/', include('authentication.urls')),
    path('profiles/', include('profiles.urls')),
]