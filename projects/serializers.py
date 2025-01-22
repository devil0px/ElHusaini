from rest_framework import serializers
from .models import Project, ProjectPhase, ProjectTeamMember, ProjectDocument

class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTeamMember
        fields = '__all__'

    def get_user_full_name(self, obj):
        return obj.user.get_full_name()

class ProjectDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectDocument
        fields = '__all__'

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else None

class ProjectPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPhase
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    phases = ProjectPhaseSerializer(many=True, read_only=True)
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True, source='projectteammember_set')
    documents = ProjectDocumentSerializer(many=True, read_only=True)
    project_manager_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_project_manager_name(self, obj):
        return obj.project_manager.get_full_name()

    def get_status_display(self, obj):
        return obj.get_status_display()
