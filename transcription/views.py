from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Meeting, Project
from .serializers import (
    MeetingSerializer, 
    MeetingUpdateSerializer,
    ProjectSerializer,
    ProjectCreateUpdateSerializer
)
from .tasks import process_meeting_uploaded_file


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing projects.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter projects by user's team
        return Project.objects.filter(team_account=self.request.user.team)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing meetings.
    Create is handled by MeetingFileUploadView.
    
    Query Parameters:
    - project_id: Filter meetings by project ID
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']  # Exclude 'post'
    
    def get_queryset(self):
        queryset = Meeting.objects.filter(project__team_account=self.request.user.team)
        
        # Filter by project_id if provided
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
            
            # If no meetings found for this project, check if project exists and is accessible
            if not queryset.exists():
                try:
                    Project.objects.get(
                        id=project_id,
                        team_account=self.request.user.team
                    )
                except Project.DoesNotExist:
                    raise serializers.ValidationError(
                        {"error": "Project not found or not accessible."}
                    )
        
        return queryset.order_by('-created_at')  # Most recent first
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return MeetingUpdateSerializer
        return MeetingSerializer


class MeetingFileUploadView(APIView):
    """
    View for uploading meeting audio files.
    """
    parser_classes = [MultiPartParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        project_id = request.data.get('project')

        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify project belongs to user's team
        try:
            project = Project.objects.get(
                id=project_id,
                team_account=request.user.team
            )
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found or not accessible."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Create meeting with project
        meeting = Meeting.objects.create(
            audio_file=file,
            status='pending',
            project=project
        )
        
        # Start processing
        process_meeting_uploaded_file.delay(meeting.id)
        
        return Response({
            "message": "Meeting file uploaded and processing started.",
            "meeting_id": meeting.id
        }, status=status.HTTP_201_CREATED)


class MeetingStatusView(APIView):
    """
    View for checking meeting processing status.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            meeting = Meeting.objects.get(
                id=file_id,
                project__team_account=request.user.team
            )
            serializer = MeetingSerializer(meeting)
            return Response(serializer.data)
        except Meeting.DoesNotExist:
            return Response(
                {"error": "Meeting not found or not accessible."}, 
                status=status.HTTP_404_NOT_FOUND
            )