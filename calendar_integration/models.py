from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CalendarConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    microsoft_token = models.JSONField()  # Store the OAuth tokens
    refresh_token = models.CharField(max_length=500)
    token_expiry = models.DateTimeField()
    flow = models.JSONField(null=True, blank=True)  # Store the OAuth flow
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'microsoft_token')