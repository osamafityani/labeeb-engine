from celery import shared_task
from datetime import datetime, timedelta
import pytz
from .services import MicrosoftCalendarService
from .models import O365Token
from bots.tasks import record_meeting
from transcription.models import Project

@shared_task
def check_upcoming_meetings():
    """
    Check for upcoming meetings and start recording them when their start time approaches.
    This task should be scheduled to run every minute.
    """
    # Get all calendar connections
    connections = O365Token.objects.all()
    
    for connection in connections:
        try:
            calendar_service = MicrosoftCalendarService(connection.user)

            # Get upcoming meetings
            meetings = calendar_service.get_upcoming_meetings()
            
            for meeting in meetings:
                # Skip if no meeting URL
                if not meeting.get('online_meeting_url'):
                    continue
                
                # Parse meeting times
                start_time = datetime.fromisoformat(meeting['start_time'].replace('Z', '+00:00'))
                now = datetime.now(pytz.UTC)
                print("start_time: ", start_time, "Now: ", now)
                # Start recording 1 minute before the meeting starts
                if timedelta(minutes=0) <= (start_time - now) <= timedelta(minutes=2):
                    # Create a project for the meeting if it doesn't exist
                    project, created = Project.objects.get_or_create(
                        title=f"Scheduled Meetings",
                        team_account=connection.user.team,
                        description=f"Automatically recorded meetings from Microsoft Calendar\n",
                    )
                    
                    # Start recording
                    record_meeting.delay(
                        meeting_url=meeting['online_meeting_url'],
                        bot_name="Auto-Recorder",
                        project_id=project.id
                    )
                    
        except Exception as e:
            print(f"Error processing meetings for user {connection.user}: {str(e)}")
            continue 