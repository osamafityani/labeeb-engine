from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from .tasks import record_meeting


class RecordMeetingView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        meeting_url = request.data.get('meeting_url')
        if request.data.get('bot_name'):
            bot_name = request.data.get('bot_name')
            record_meeting.delay(meeting_url, bot_name)
        else:
            record_meeting.delay(meeting_url)
        return Response({"message": "Meeting is being recorded..."})


