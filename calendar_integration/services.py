from datetime import datetime, timezone, timedelta
import pytz
from O365 import Account, MSGraphProtocol
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MicrosoftCalendarService:
    def __init__(self):
        self.client_id = settings.MS_CLIENT_ID
        self.client_secret = settings.MS_CLIENT_SECRET
        self.redirect_uri = settings.MS_REDIRECT_URI
        self.scopes = ['https://graph.microsoft.com/Calendars.Read']
        self.protocol = MSGraphProtocol()  # Use MS Graph protocol
        
    def get_authorization_url(self):
        """Generate OAuth URL and flow dict for user"""
        account = Account((self.client_id, self.client_secret), protocol=self.protocol)
        auth_url, flow = account.connection.get_authorization_url(
            requested_scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )
        return auth_url, flow
    
    def get_tokens_from_code(self, flow, authorization_response_url):
        """Exchange authorization code for tokens using flow dict"""
        account = Account((self.client_id, self.client_secret), protocol=self.protocol)
        success = account.connection.request_token(
            authorization_url=authorization_response_url,
            flow=flow
        )

        if not success:
            raise Exception("Failed to exchange code for tokens")
        
        # Get the token from the connection
        token = account.connection.token_backend.token
        if not token:
            raise Exception("Failed to get token after successful exchange")
            
        return token
    
    def _get_account_with_token(self, connection):
        """Get an authenticated account instance using stored tokens"""
        account = Account((self.client_id, self.client_secret), protocol=self.protocol)
        
        # Set the token in the connection
        account.connection.token_backend.token = connection.microsoft_token
        
        # Check if token needs refresh
        if connection.token_expiry and connection.token_expiry <= datetime.now(timezone.utc):
            try:
                # Attempt to refresh the token
                account.connection.refresh_token()
                # Update the stored token
                connection.microsoft_token = account.connection.token_backend.token
                connection.token_expiry = datetime.fromtimestamp(
                    account.connection.token_backend.token.get('expires_at', 0),
                    timezone.utc
                )
                connection.save()
            except Exception as e:
                logger.error(f"Failed to refresh token: {str(e)}")
                raise Exception("Token refresh failed")
        
        return account
    
    def get_upcoming_meetings(self, connection):
        """Get upcoming meetings for a user"""
        try:
            account = self._get_account_with_token(connection)
            
            # Get the schedule and default calendar
            schedule = account.schedule()
            calendar = schedule.get_default_calendar()
            
            if not calendar:
                raise Exception("No default calendar found")
            
            # Get events for next 24 hours
            now = datetime.now(pytz.UTC)
            end_time = now + timedelta(days=1)
            
            # Query events
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
                    online_meeting_url = None
                    
                    # Check for Teams meeting URL
                    if hasattr(event, 'online_meeting_url') and event.online_meeting_url:
                        has_video = True
                        online_meeting_url = event.online_meeting_url
                    # Check for meeting URL in body
                    elif hasattr(event, 'body') and event.body:
                        body_lower = event.body.lower()
                        if 'teams' in body_lower or 'zoom' in body_lower:
                            has_video = True
                            # Try to extract URL from body
                            import re
                            url_match = re.search(r'https?://[^\s<>"]+|www\.[^\s<>"]+', event.body)
                            if url_match:
                                online_meeting_url = url_match.group(0)
                    
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
                            'online_meeting_url': online_meeting_url,
                            'description': event.body if hasattr(event, 'body') else None
                        }
                        meetings.append(meeting)
                except Exception as e:
                    logger.error(f"Error processing event: {str(e)}")
                    continue
            
            return meetings
            
        except Exception as e:
            logger.error(f"Error getting meetings: {str(e)}")
            raise