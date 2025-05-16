from django.contrib import admin
from .models import Team

models = [Team]
admin.site.register(models)
