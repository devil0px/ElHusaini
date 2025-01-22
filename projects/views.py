from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Project, ProjectPhase, ProjectTeamMember, ProjectDocument
from .forms import ProjectForm, ProjectPhaseForm, ProjectTeamMemberForm, ProjectDocumentForm

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Project.objects.all().order_by('-created_at')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
            
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.prefetch_related('phases')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = Project.objects.all()
        
        # إحصائيات المشاريع
        context['total_projects'] = projects.count()
        context['active_projects'] = projects.filter(status='in_progress').count()
        context['completed_projects'] = projects.filter(status='completed').count()
        context['delayed_projects'] = projects.filter(
            end_date__lt=timezone.now().date(),
            status__in=['planning', 'in_progress', 'on_hold']
        ).count()
        
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context['phases'] = project.phases.all()
        context['team_members'] = project.project_team_members.select_related('user').all()
        context['documents'] = project.documents.all()
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('web_projects:project_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء المشروع بنجاح.')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('web_projects:project_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المشروع بنجاح.')
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('web_projects:project_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المشروع بنجاح.')
        return super().delete(request, *args, **kwargs)

class ProjectPhaseCreateView(LoginRequiredMixin, CreateView):
    model = ProjectPhase
    form_class = ProjectPhaseForm
    template_name = 'projects/phase_form.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_id']
        messages.success(self.request, 'تم إنشاء المرحلة بنجاح.')
        return super().form_valid(form)

class ProjectPhaseUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectPhase
    form_class = ProjectPhaseForm
    template_name = 'projects/phase_form.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المرحلة بنجاح.')
        return super().form_valid(form)

class ProjectPhaseDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectPhase
    template_name = 'projects/phase_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المرحلة بنجاح.')
        return super().delete(request, *args, **kwargs)

class ProjectTeamMemberCreateView(LoginRequiredMixin, CreateView):
    model = ProjectTeamMember
    form_class = ProjectTeamMemberForm
    template_name = 'projects/team_member_form.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_id']
        messages.success(self.request, 'تم إضافة عضو الفريق بنجاح.')
        return super().form_valid(form)

class ProjectTeamMemberUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectTeamMember
    form_class = ProjectTeamMemberForm
    template_name = 'projects/team_member_form.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث عضو الفريق بنجاح.')
        return super().form_valid(form)

class ProjectTeamMemberDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectTeamMember
    template_name = 'projects/team_member_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف عضو الفريق بنجاح.')
        return super().delete(request, *args, **kwargs)

class ProjectDocumentCreateView(LoginRequiredMixin, CreateView):
    model = ProjectDocument
    form_class = ProjectDocumentForm
    template_name = 'projects/document_form.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_id']
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'تم رفع المستند بنجاح.')
        return super().form_valid(form)

class ProjectDocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectDocument
    form_class = ProjectDocumentForm
    template_name = 'projects/document_form.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المستند بنجاح.')
        return super().form_valid(form)

class ProjectDocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectDocument
    template_name = 'projects/document_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('web_projects:project_detail', kwargs={'pk': self.object.project.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المستند بنجاح.')
        return super().delete(request, *args, **kwargs)

def project_progress_report(request):
    projects = Project.objects.all()
    data = []
    for project in projects:
        completed_phases = project.phases.filter(completion_percentage=100).count()
        total_phases = project.phases.count()
        progress = (completed_phases / total_phases * 100) if total_phases > 0 else 0
        
        data.append({
            'id': project.id,
            'name': project.name,
            'progress': progress,
            'total_phases': total_phases,
            'completed_phases': completed_phases,
            'budget': project.budget,
            'actual_cost': project.actual_cost
        })
    
    return render(request, 'projects/project_progress_report.html', {
        'projects': data
    })

def project_timeline_report(request):
    projects = Project.objects.all()
    timeline_data = []
    for project in projects:
        phases = project.phases.all().order_by('start_date')
        timeline_data.append({
            'project': project,
            'phases': phases
        })
    
    return render(request, 'projects/project_timeline_report.html', {
        'timeline_data': timeline_data
    })
