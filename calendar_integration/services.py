from datetime import datetime, timezone, time
import pytz
from O365 import Account
from django.conf import settings
from .o365_token_backend import DjangoTokenBackend

class MicrosoftCalendarService:
    def __init__(self, user):
        self.client_id = settings.MS_CLIENT_ID
        self.client_secret = settings.MS_CLIENT_SECRET
        self.redirect_uri = settings.MS_REDIRECT_URI
        self.scopes = ['https://graph.microsoft.com/Calendars.Read']
        self.user = user

    def get_account(self):
        credentials = (self.client_id, self.client_secret)
        token_backend = DjangoTokenBackend(self.user)
        account = Account(
            credentials,
            token_backend=token_backend,
            auth_flow_type='authorization',
            tenant_id='common',
        )
        return account
        
    def get_authorization_url(self):
        """Generate OAuth URL and flow dict for user"""
        account = self.get_account()
        auth_url, flow = account.connection.get_authorization_url(
            requested_scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )
        # Return both URL and flow dict
        return auth_url, flow
    
    def get_tokens_from_code(self, flow, authorization_response_url):
        """Exchange authorization code for tokens using flow dict"""
        account = self.get_account()
        success = account.connection.request_token(
            authorization_url=authorization_response_url,
            flow=flow
        )

        return success
    
    def get_upcoming_meetings(self):
        """Get upcoming meetings for a user"""
        account = self.get_account()   

        schedule = account.schedule()
        response = account.connection.get(
            'https://graph.microsoft.com/v1.0/me/calendar',
            params={
                '$select': 'id,name'  # Exclude problematic fields
            }
        )
        
        # Step 3: Create a Calendar object manually from response
        from O365.calendar import Calendar

        calendar_data = response.json()
        calendar = Calendar(parent=schedule, **calendar_data) 

        # Get events for next 24 hours
        now = datetime.now(pytz.UTC)
        # End of the current day in UTC (23:59:59.999999)
        end_time = datetime.combine(now.date(), time.max).replace(tzinfo=pytz.UTC)
        
        events = calendar.get_events(start_recurring=now, end_recurring=end_time, include_recurring=True)
        
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