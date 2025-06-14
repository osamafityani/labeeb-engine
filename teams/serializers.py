from rest_framework import serializers
from .models import Team, TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'team', 'name', 'created_at', 'last_modified']
        read_only_fields = ['created_at', 'last_modified']


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True, source='teammember_set')
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'company', 'created_at', 'last_modified', 'members', 'member_count']
        read_only_fields = ['created_at', 'last_modified']

    def get_member_count(self, obj):
        return obj.teammember_set.count()


class TeamDetailSerializer(TeamSerializer):
    """
    Extended Team serializer that includes full member details
    Use this for detailed team views
    """
    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + []  # Add any additional fields specific to detailed view


class TeamCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating teams
    Excludes read-only fields that are auto-generated
    """
    class Meta:
        model = Team
        fields = ['name', 'company']
