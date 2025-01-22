from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, F
from .models import Contract, ContractClause, ContractPayment
from .forms import ContractForm, ContractClauseForm, ContractPaymentForm
from clients.models import Client
from projects.models import Project

class ContractListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Contract
    permission_required = 'contracts.view_contract'
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contract_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        contract_type = self.request.GET.get('contract_type')
        
        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(title__icontains=search) |
                Q(client__name__icontains=search) |
                Q(project__name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
            
        return queryset.select_related('client', 'project')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        context['projects'] = Project.objects.all()
        return context

class ContractDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Contract
    permission_required = 'contracts.view_contract'
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = self.get_object()
        
        # Get contract clauses
        context['clauses'] = contract.clauses.all()
        
        # Get payments
        context['payments'] = contract.payments.all()
        
        # Calculate totals
        total_paid = contract.payments.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        context['total_paid'] = total_paid
        context['balance'] = contract.total_value - total_paid
        
        return context

class ContractCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Contract
    permission_required = 'contracts.add_contract'
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:contract-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إنشاء العقد بنجاح.')
        return super().form_valid(form)

class ContractUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Contract
    permission_required = 'contracts.change_contract'
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:contract-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث العقد بنجاح.')
        return super().form_valid(form)

class ContractDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Contract
    permission_required = 'contracts.delete_contract'
    template_name = 'contracts/contract_confirm_delete.html'
    success_url = reverse_lazy('contracts:contract-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف العقد بنجاح.')
        return super().delete(request, *args, **kwargs)

class ContractClauseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ContractClause
    permission_required = 'contracts.view_contractclause'
    template_name = 'contracts/clause_list.html'
    context_object_name = 'clauses'
    paginate_by = 10

    def get_queryset(self):
        return ContractClause.objects.filter(contract_id=self.kwargs['contract_pk'])

class ContractClauseDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ContractClause
    permission_required = 'contracts.view_contractclause'
    template_name = 'contracts/clause_detail.html'
    context_object_name = 'clause'

class ContractClauseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ContractClause
    permission_required = 'contracts.add_contractclause'
    form_class = ContractClauseForm
    template_name = 'contracts/clause_form.html'

    def get_success_url(self):
        return reverse_lazy('contracts:contract-detail', kwargs={'pk': self.object.contract.pk})

    def form_valid(self, form):
        form.instance.contract_id = self.kwargs['contract_pk']
        messages.success(self.request, 'تم إضافة البند بنجاح.')
        return super().form_valid(form)

class ContractClauseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ContractClause
    permission_required = 'contracts.change_contractclause'
    form_class = ContractClauseForm
    template_name = 'contracts/clause_form.html'

    def get_success_url(self):
        return reverse_lazy('contracts:contract-detail', kwargs={'pk': self.object.contract.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث البند بنجاح.')
        return super().form_valid(form)

class ContractClauseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ContractClause
    permission_required = 'contracts.delete_contractclause'
    template_name = 'contracts/clause_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('contracts:contract-detail', kwargs={'pk': self.object.contract.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف البند بنجاح.')
        return super().delete(request, *args, **kwargs)

class ContractPaymentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ContractPayment
    permission_required = 'contracts.view_contractpayment'
    template_name = 'contracts/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        return ContractPayment.objects.filter(contract_id=self.kwargs['contract_pk'])

class ContractPaymentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ContractPayment
    permission_required = 'contracts.view_contractpayment'
    template_name = 'contracts/payment_detail.html'
    context_object_name = 'payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        context['contract'] = payment.contract
        return context

class ContractPaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ContractPayment
    permission_required = 'contracts.add_contractpayment'
    form_class = ContractPaymentForm
    template_name = 'contracts/payment_form.html'

    def get_success_url(self):
        return reverse_lazy('contracts:contract-detail', kwargs={'pk': self.object.contract.pk})

    def form_valid(self, form):
        form.instance.contract_id = self.kwargs['contract_pk']
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إضافة الدفعة بنجاح.')
        return super().form_valid(form)

class ContractPaymentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ContractPayment
    permission_required = 'contracts.change_contractpayment'
    form_class = ContractPaymentForm
    template_name = 'contracts/payment_form.html'

    def get_success_url(self):
        return reverse_lazy('contracts:contract-detail', kwargs={'pk': self.object.contract.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الدفعة بنجاح.')
        return super().form_valid(form)

class ContractPaymentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ContractPayment
    permission_required = 'contracts.delete_contractpayment'
    template_name = 'contracts/payment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('contracts:contract-detail', kwargs={'pk': self.object.contract.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الدفعة بنجاح.')
        return super().delete(request, *args, **kwargs)
