from rest_framework import serializers
from .models import Meeting, Project, ActionItem


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


class ActionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionItem
        fields = ['id', 'text', 'due_by', 'completed', 'meeting', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ActionItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionItem
        fields = ['text', 'due_by', 'completed', 'meeting']


class MeetingSerializer(serializers.ModelSerializer):
    action_items = ActionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'project', 'audio_file', 'transcription_file', 'embeddings', 'status', 'timestamp', 'created_at', 'summary', 'action_items']
        read_only_fields = ['audio_file', 'transcription_file', 'embeddings', 'status', 'timestamp', 'action_items']


class MeetingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['title', 'project', 'summary']  # Allow updating title, project, and summary



