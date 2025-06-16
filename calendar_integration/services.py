from datetime import datetime, timezone
import pytz
from O365 import Account
from django.conf import settings

class MicrosoftCalendarService:
    def __init__(self):
        self.client_id = settings.MS_CLIENT_ID
        self.client_secret = settings.MS_CLIENT_SECRET
        self.redirect_uri = settings.MS_REDIRECT_URI
        self.scopes = ['https://graph.microsoft.com/Calendars.Read']
        
    def get_authorization_url(self):
        """Generate OAuth URL and flow dict for user"""
        account = Account((self.client_id, self.client_secret))
        auth_url, flow = account.connection.get_authorization_url(
            requested_scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )
        # Return both URL and flow dict
        return auth_url, flow
    
    def get_tokens_from_code(self, flow, authorization_response_url):
        """Exchange authorization code for tokens using flow dict"""
        account = Account((self.client_id, self.client_secret))
        token = account.connection.request_token(
            authorization_url=authorization_response_url,
            flow=flow
        )
        return token
    
    def get_upcoming_meetings(self, connection):
        """Get upcoming meetings for a user"""
        account = Account((self.client_id, self.client_secret))
        account.connection.token_backend.token = connection.microsoft_token
        
        schedule = account.schedule()
        calendar = schedule.get_default_calendar()
        
        # Get events for next 24 hours
        now = datetime.now(pytz.UTC)
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        events = calendar.get_events(
            start=now,
            end=end_time,
            include_recurring=True
        )
        
        meetings = []
        for event in events:
            try:
                # Convert all datetime objects to UTC
                start_time = event.start.astimezone(pytz.UTC)
                end_time = event.end.astimezone(pytz.UTC)
                
                # Check if event has video conferencing
                has_video = False
                if hasattr(event, 'online_meeting_url') and event.online_meeting_url:
                    has_video = True
                elif hasattr(event, 'body') and event.body and ('teams' in event.body.lower() or 'zoom' in event.body.lower()):
                    has_video = True
                
                if has_video:
                    meeting = {
                        'id': event.object_id,
                        'title': event.subject,
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'organizer': event.organizer.get('emailAddress', {}).get('address', 'Unknown'),
                        'attendees': [
                            attendee.get('emailAddress', {}).get('address', 'Unknown')
                            for attendee in event.attendees
                        ] if hasattr(event, 'attendees') else [],
                        'online_meeting_url': event.online_meeting_url if hasattr(event, 'online_meeting_url') else None,
                        'description': event.body if hasattr(event, 'body') else None
                    }
                    meetings.append(meeting)
            except Exception as e:
                continue
        
        return meetings