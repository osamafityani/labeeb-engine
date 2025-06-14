from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CalendarConnection
from .services import MicrosoftCalendarService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auth_url(request):
    """Get Microsoft OAuth URL for the user"""
    calendar_service = MicrosoftCalendarService()
    auth_url = calendar_service.get_authorization_url(request.user)
    return JsonResponse({'auth_url': auth_url})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_callback(request):
    """Handle OAuth callback and store tokens"""
    code = request.data.get('code')
    if not code:
        return JsonResponse({'error': 'No code provided'}, status=400)
    
    calendar_service = MicrosoftCalendarService()
    tokens = calendar_service.get_tokens_from_code(code)
    
    # Store tokens in database
    CalendarConnection.objects.update_or_create(
        user=request.user,
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