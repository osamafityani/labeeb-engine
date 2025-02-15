from django.urls import path
from . import views

urlpatterns = [
    path('get_profile/', views.get_profile, name='get_profile'),
    path('set_country/', views.set_country, name='set_country'),
    path('set_first_name/', views.set_first_name, name='set_first_name'),
    path('set_last_name/', views.set_last_name, name='set_last_name'),
    path('set_birth_date/', views.set_birth_date, name='set_birth_date'),
    # add other URL patterns here
]
