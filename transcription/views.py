from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import Meeting
from .serializers import MeetingSerializer
from .tasks import process_meeting_uploaded_file


class MeetingFileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        print(request.FILES)
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided."}, status=400)

        uploaded_file = Meeting.objects.create(audio_file=file, status='pending')
        process_meeting_uploaded_file.delay(uploaded_file.id)
        return Response({"message": "Meeting file uploaded and processing started.", "file_id": uploaded_file.id})


class MeetingStatusView(APIView):
    def get(self, request, file_id):
        try:
            meeting = Meeting.objects.get(id=file_id)
            serializer = MeetingSerializer(meeting)
            return Response(serializer.data)
        except Meeting.DoesNotExist:
            return Response({"error": "Meeting not found."}, status=404)