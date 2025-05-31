from celery import shared_task
from django.core.files.base import ContentFile
from .utils import transcription_pipeline, summarize, embedding_pipeline
from datetime import datetime
import uuid


@shared_task
def process_meeting_uploaded_file(meeting_id):
    from .models import Meeting
    meeting = Meeting.objects.get(id=meeting_id)

    transcription = transcription_pipeline(meeting.audio_file.path)
    summary, meeting_title = summarize(transcription, project=meeting.project)
    
    # Create a unique filename using timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:4]
    filename = f"transcription_{meeting_id}_{timestamp}_{unique_id}.txt"
    
    meeting.transcription_file.save(filename, ContentFile(summary), save=False)
    meeting.title = meeting_title
    meeting.summary = summary  # Save the summary in the model

    embeddings = embedding_pipeline(transcription)
    meeting.embeddings = embeddings

    meeting.status = 'completed'
    meeting.save()
