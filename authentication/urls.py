"""
Authentication URLs Configuration

All responses follow the format:
{
    "status": "success" | "error",
    "message": "Human readable message",
    "data": {
        // Endpoint specific data
    }
}
"""

from django.urls import path, include
from . import views

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', views.login_view, name='login'),  # POST: email, password
    path('logout/', views.logout_view, name='logout'),  # POST: Requires Token
    path('signup/', views.signup_view, name='signup'),  # POST: email, password, first_name, last_name
    path('delete_account/', views.delete_account, name='delete_account'),  # POST: Requires Token
]
