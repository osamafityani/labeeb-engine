from django.conf import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import CalendarConnection
from .services import MicrosoftCalendarService
from django.urls import reverse
from rest_framework import status

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auth_url(request):
    """Get Microsoft OAuth URL for the user"""
    calendar_service = MicrosoftCalendarService(request.user)
    state = str(request.user.id)  # You can keep this or generate a random state string
    
    auth_url, flow = calendar_service.get_authorization_url()
    auth_url = auth_url.replace(f'state={flow["state"]}', f'state={state}')
    flow['state'] = state
    flow['auth_uri'] = auth_url
    # Store flow in CalendarConnection
    CalendarConnection.objects.update_or_create(
        user=request.user,
        defaults={'flow': flow}
    )

    if flow is None:
        return JsonResponse({'message': "Flow is None"})
    
    return JsonResponse({'auth_url': auth_url, 'flow': str(flow)})


@api_view(['GET'])
def handle_callback(request):
    """Handle OAuth callback and store tokens"""
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code or not state:
        return JsonResponse({'error': 'No code or state provided'}, status=400)
    
    try:
        user = User.objects.get(id=state)
        connection = CalendarConnection.objects.get(user=user)
        flow = connection.flow
    except (User.DoesNotExist, CalendarConnection.DoesNotExist):
        return JsonResponse({'error': 'Invalid state parameter or no flow found'}, status=400)
    
    calendar_service = MicrosoftCalendarService(user)
    
    # Build full redirect URL from request (including code and state)
    redirect_response_url = request.build_absolute_uri()
    
    success = calendar_service.get_tokens_from_code(flow, redirect_response_url)
    
    if success:
        return Response({"status": 'success'}, status=status.HTTP_200_OK)
    else:
        return Response({"status": 'failure'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upcoming_meetings(request):
    """Get user's upcoming meetings"""
    try:
        calendar_service = MicrosoftCalendarService(request.user)
        meetings = calendar_service.get_upcoming_meetings()

        return JsonResponse({'meetings': meetings})
    except CalendarConnection.DoesNotExist:
        return JsonResponse({'error': 'Calendar not connected'}, status=404)