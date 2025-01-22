from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    # إدارة العقود
    path('', views.ContractListView.as_view(), name='contract-list'),
    path('create/', views.ContractCreateView.as_view(), name='contract-create'),
    path('<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
    path('<int:pk>/update/', views.ContractUpdateView.as_view(), name='contract-update'),
    path('<int:pk>/delete/', views.ContractDeleteView.as_view(), name='contract-delete'),
    
    # بنود العقود
    path('<int:contract_pk>/clauses/', views.ContractClauseListView.as_view(), name='contract-clause-list'),
    path('<int:contract_pk>/clauses/create/', views.ContractClauseCreateView.as_view(), name='contract-clause-create'),
    path('clauses/<int:pk>/', views.ContractClauseDetailView.as_view(), name='contract-clause-detail'),
    path('clauses/<int:pk>/update/', views.ContractClauseUpdateView.as_view(), name='contract-clause-update'),
    path('clauses/<int:pk>/delete/', views.ContractClauseDeleteView.as_view(), name='contract-clause-delete'),
    
    # المدفوعات
    path('<int:contract_pk>/payments/', views.ContractPaymentListView.as_view(), name='contract-payment-list'),
    path('<int:contract_pk>/payments/create/', views.ContractPaymentCreateView.as_view(), name='contract-payment-create'),
    path('payments/<int:pk>/', views.ContractPaymentDetailView.as_view(), name='contract-payment-detail'),
    path('payments/<int:pk>/update/', views.ContractPaymentUpdateView.as_view(), name='contract-payment-update'),
    path('payments/<int:pk>/delete/', views.ContractPaymentDeleteView.as_view(), name='contract-payment-delete'),
]
