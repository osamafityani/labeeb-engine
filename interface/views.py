from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from interface.utils import ask as ask_util
from openai import OpenAI


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask(request):
    # Check if the request body contains the expected data
    if 'query' not in request.data:
        return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Get the string from the request body
    query = request.data['query']
    
    # Get user's team ID
    user_team_id = request.user.team.id if request.user.team else None
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Call ask function with user's team ID
    result = ask_util(client, query, user_team_id=user_team_id)

    return Response({"answer": result}, status=status.HTTP_200_OK)
