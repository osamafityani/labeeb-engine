from django.contrib import admin
from .models import Meeting

models = [Meeting]
admin.site.register(models)
