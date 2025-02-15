from django.db import models


class Meeting(models.Model):
    # user = models.ForeignKey()  # TODO: Add user model
    team = models.CharField(max_length=100, default='', blank=True, null=True)
    project = models.CharField(max_length=100, default='', blank=True, null=True)
    audio_file = models.FileField(upload_to='uploads/')
    transcription_file = models.FileField(upload_to='uploads/')
    embeddings = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
