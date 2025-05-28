from rest_framework import serializers
from .models import Meeting, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'team_account', 'team', 'type', 'code', 'start_date', 'end_date']


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'code', 'start_date', 'end_date']

    def create(self, validated_data):
        # Set the team_account from the authenticated user's team
        user = self.context['request'].user
        validated_data['team_account'] = user.team
        return super().create(validated_data)


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'title', 'project', 'audio_file', 'transcription_file', 'embeddings', 'status', 'timestamp', 'created_at', 'summary']
        read_only_fields = ['audio_file', 'transcription_file', 'embeddings', 'status', 'timestamp']


class MeetingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['title', 'project', 'summary']  # Allow updating title, project, and summary
