from django.db import models
from pgvector.django import VectorField
from transcription.tasks import process_meeting_uploaded_file
from teams.models import Team
import datetime


class Project(models.Model):
    title = models.CharField(max_length=250, default='', blank=True, null=True)
    description = models.CharField(max_length=1000, default='', blank=True, null=True)
    team_account = models.ForeignKey(Team, related_name='team', on_delete=models.CASCADE)
    team = models.CharField(max_length=100, default='', blank=True, null=True)
    type = models.CharField(max_length=50, default='', blank=True, null=True)
    code = models.CharField(max_length=50, default='', blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)


class Meeting(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=250, default='', blank=True, null=True)
    project = models.ForeignKey(Project, related_name='project', on_delete=models.CASCADE, null=True)
    audio_file = models.FileField(upload_to='uploads/')
    transcription_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    embeddings = VectorField(dimensions=1536, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        print(f"audio file {self.audio_file} embeddings {self.embeddings}")
        if self.audio_file and not self.embeddings:
            print(f"Task created for meeting {self.pk}")
            process_meeting_uploaded_file.delay(self.pk)
            super(Meeting, self).save(*args, **kwargs)
        else:
            super(Meeting, self).save(*args, **kwargs)
