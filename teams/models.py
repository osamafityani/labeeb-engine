from django.db import models


class Team(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    name = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)