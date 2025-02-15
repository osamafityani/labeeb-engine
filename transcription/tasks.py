from celery import shared_task
from django.core.files.base import ContentFile
from .utils import transcription_pipeline, summarize, embedding_pipeline
from .models import Meeting


@shared_task
def process_meeting_uploaded_file(file_id):
    meeting = Meeting.objects.get(id=file_id)

    transcription = transcription_pipeline(meeting.audio_file.path)
    meeting.transcription_file.save("transcription.txt", ContentFile(summarize(transcription)))  # TODO: randomize file naming

    embeddings = embedding_pipeline(transcription)
    meeting.embeddings = embeddings

    meeting.status = 'completed'
    meeting.save()
