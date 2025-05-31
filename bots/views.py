from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from .tasks import record_meeting


class RecordMeetingView(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        meeting_url = request.data.get('meeting_url')
        project_id = request.data.get('project_id')
        
        if not meeting_url or not project_id:
            return Response({
                "error": "meeting_url and project_id are required"
            }, status=400)

        # Get team from authenticated user
        team = request.user.team
        if not team:
            return Response({
                "error": "User is not associated with any team"
            }, status=400)

        bot_name = request.data.get('bot_name', 'Faris2')
        
        # Pass team_id and project_id to the Celery task
        record_meeting.delay(
            meeting_url=meeting_url,
            bot_name=bot_name,
            team_id=team.id,
            project_id=project_id
        )
        
        return Response({"message": "Meeting is being recorded..."})


