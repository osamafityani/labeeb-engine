from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CalendarConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    microsoft_token = models.JSONField(null=True, blank=True)  # Store the OAuth tokens
    refresh_token = models.CharField(max_length=500, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    flow = models.JSONField(null=True, blank=True)  # Store the OAuth flow
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'microsoft_token')

class O365Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.JSONField()
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"O365Token for {self.user}"