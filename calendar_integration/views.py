from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import CalendarConnection
from .services import MicrosoftCalendarService
import json

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auth_url(request):
    """Get Microsoft OAuth URL for the user"""
    calendar_service = MicrosoftCalendarService()
    # Include user ID in state parameter as JSON
    state = json.dumps({'user_id': str(request.user.id)})
    auth_url = calendar_service.get_authorization_url(request.user, state=state)
    return JsonResponse({'auth_url': auth_url})

@api_view(['GET'])
def handle_callback(request):
    """Handle OAuth callback and store tokens"""
    code = request.GET.get('code')
    state = request.GET.get('state')  # This will contain the JSON with user ID
    
    if not code or not state:
        return JsonResponse({'error': 'No code or state provided'}, status=400)
    
    try:
        # Parse the state JSON to get user ID
        state_data = json.loads(state)
        user_id = state_data.get('user_id')
        if not user_id:
            raise ValueError("No user_id in state")
            
        user = User.objects.get(id=user_id)
    except (json.JSONDecodeError, ValueError, User.DoesNotExist) as e:
        return JsonResponse({'error': f'Invalid state parameter: {str(e)}'}, status=400)
    
    calendar_service = MicrosoftCalendarService()
    tokens = calendar_service.get_tokens_from_code(code)
    
    # Store tokens in database
    CalendarConnection.objects.update_or_create(
        user=user,
        defaults={
            'microsoft_token': tokens,
            'refresh_token': tokens.get('refresh_token'),
            'token_expiry': tokens.get('expires_at')
        }
    )
    
    return JsonResponse({'status': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upcoming_meetings(request):
    """Get user's upcoming meetings"""
    try:
        connection = CalendarConnection.objects.get(user=request.user)
        calendar_service = MicrosoftCalendarService()
        meetings = calendar_service.get_upcoming_meetings(connection)
        return JsonResponse({'meetings': meetings})
    except CalendarConnection.DoesNotExist:
        return JsonResponse({'error': 'Calendar not connected'}, status=404)