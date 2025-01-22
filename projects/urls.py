from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project URLs
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # Phase URLs
    path('<int:project_id>/phases/create/', views.ProjectPhaseCreateView.as_view(), name='phase_create'),
    path('phases/<int:pk>/update/', views.ProjectPhaseUpdateView.as_view(), name='phase_update'),
    path('phases/<int:pk>/delete/', views.ProjectPhaseDeleteView.as_view(), name='phase_delete'),
    
    # Team Member URLs
    path('<int:project_id>/team/create/', views.ProjectTeamMemberCreateView.as_view(), name='team_member_create'),
    path('team/<int:pk>/update/', views.ProjectTeamMemberUpdateView.as_view(), name='team_member_update'),
    path('team/<int:pk>/delete/', views.ProjectTeamMemberDeleteView.as_view(), name='team_member_delete'),
    
    # Document URLs
    path('<int:project_id>/documents/create/', views.ProjectDocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/update/', views.ProjectDocumentUpdateView.as_view(), name='document_update'),
    path('documents/<int:pk>/delete/', views.ProjectDocumentDeleteView.as_view(), name='document_delete'),
]
