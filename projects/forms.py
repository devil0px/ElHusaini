from django import forms
from .models import Project, ProjectTeamMember, ProjectPhase, ProjectDocument

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'description', 'location',
            'start_date', 'end_date', 'status',
            'project_manager', 'budget'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProjectTeamMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectTeamMember
        fields = ['user', 'member_role', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ProjectPhaseForm(forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = [
            'name', 'description', 'start_date',
            'end_date', 'completion_percentage', 'budget'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ['title', 'document_type', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
