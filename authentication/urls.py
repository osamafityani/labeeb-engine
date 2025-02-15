from django.urls import path, include
from . import views

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    # add other URL patterns here
]
