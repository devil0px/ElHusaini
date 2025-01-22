from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # إدارة العملاء
    path('', views.ClientListView.as_view(), name='client-list'),
    path('create/', views.ClientCreateView.as_view(), name='client-create'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('<int:pk>/update/', views.ClientUpdateView.as_view(), name='client-update'),
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client-delete'),
    
    # جهات الاتصال للعملاء
    path('<int:client_pk>/contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('<int:client_pk>/contacts/create/', views.ContactCreateView.as_view(), name='contact-create'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/<int:pk>/update/', views.ContactUpdateView.as_view(), name='contact-update'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact-delete'),
]
