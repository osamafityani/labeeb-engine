from django.db import models
from pgvector.django import VectorField
from transcription.tasks import process_meeting_uploaded_file


class Meeting(models.Model):
    # user = models.ForeignKey()  # TODO: Add user model
    team = models.CharField(max_length=100, default='', blank=True, null=True)
    project = models.CharField(max_length=100, default='', blank=True, null=True)
    audio_file = models.FileField(upload_to='uploads/')
    transcription_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    embeddings = VectorField(dimensions=1536, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        print(f"audio file {self.audio_file} embeddings {self.embeddings}")
        if self.audio_file and not self.embeddings:
            print(f"Task created for meeting {self.pk}")
            process_meeting_uploaded_file.delay(self.pk)
            super(Meeting, self).save(*args, **kwargs)
