from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import (
    Department, Position, Employee, Attendance,
    Leave, Payroll, Document
)
from .forms import (
    DepartmentForm, PositionForm, EmployeeForm,
    AttendanceForm, LeaveForm, PayrollForm, DocumentForm
)

# Department Views
class DepartmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Department
    permission_required = 'hr.view_department'
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(manager__first_name__icontains=search) |
                Q(manager__last_name__icontains=search)
            )
        return queryset

class DepartmentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Department
    permission_required = 'hr.view_department'
    template_name = 'hr/department_detail.html'
    context_object_name = 'department'

class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Department
    permission_required = 'hr.add_department'
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء القسم بنجاح.')
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Department
    permission_required = 'hr.change_department'
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث القسم بنجاح.')
        return super().form_valid(form)

class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Department
    permission_required = 'hr.delete_department'
    template_name = 'hr/department_confirm_delete.html'
    success_url = reverse_lazy('hr:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف القسم بنجاح.')
        return super().delete(request, *args, **kwargs)

# Position Views
class PositionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Position
    permission_required = 'hr.view_position'
    template_name = 'hr/position_list.html'
    context_object_name = 'positions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(department__name__icontains=search)
            )
        if department:
            queryset = queryset.filter(department_id=department)
            
        return queryset.select_related('department')

class PositionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Position
    permission_required = 'hr.view_position'
    template_name = 'hr/position_detail.html'
    context_object_name = 'position'

class PositionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Position
    permission_required = 'hr.add_position'
    form_class = PositionForm
    template_name = 'hr/position_form.html'
    success_url = reverse_lazy('hr:position_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الوظيفة بنجاح.')
        return super().form_valid(form)

class PositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Position
    permission_required = 'hr.change_position'
    form_class = PositionForm
    template_name = 'hr/position_form.html'
    success_url = reverse_lazy('hr:position_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الوظيفة بنجاح.')
        return super().form_valid(form)

class PositionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Position
    permission_required = 'hr.delete_position'
    template_name = 'hr/position_confirm_delete.html'
    success_url = reverse_lazy('hr:position_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الوظيفة بنجاح.')
        return super().delete(request, *args, **kwargs)

# Employee Views
class EmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Employee
    permission_required = 'hr.view_employee'
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        position = self.request.GET.get('position')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(employee_id__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(national_id__icontains=search)
            )
        if department:
            queryset = queryset.filter(position__department_id=department)
        if position:
            queryset = queryset.filter(position_id=position)
        if status:
            queryset = queryset.filter(is_active=status == 'active')
            
        return queryset.select_related('user', 'position', 'position__department')

class EmployeeDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Employee
    permission_required = 'hr.view_employee'
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        
        # Get recent attendance records
        context['recent_attendance'] = employee.attendance_records.all()[:5]
        
        # Get active leaves
        context['active_leaves'] = employee.leaves.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )
        
        # Get recent documents
        context['recent_documents'] = employee.documents.all()[:5]
        
        # Get latest payroll
        try:
            context['latest_payroll'] = employee.payrolls.latest('year', 'month')
        except Payroll.DoesNotExist:
            context['latest_payroll'] = None
            
        return context

class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Employee
    permission_required = 'hr.add_employee'
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة الموظف بنجاح')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء إضافة الموظف')
        return super().form_invalid(form)

class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Employee
    permission_required = 'hr.change_employee'
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث بيانات الموظف بنجاح')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'حدث خطأ أثناء تحديث بيانات الموظف')
        return super().form_invalid(form)

class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Employee
    permission_required = 'hr.delete_employee'
    template_name = 'hr/employee_confirm_delete.html'
    success_url = reverse_lazy('hr:employee_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الموظف بنجاح')
        return super().delete(request, *args, **kwargs)

# Attendance Views
class AttendanceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Attendance
    permission_required = 'hr.add_attendance'
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تسجيل الحضور بنجاح')
        return super().form_valid(form)

class AttendanceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Attendance
    permission_required = 'hr.view_attendance'
    template_name = 'hr/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        status = self.request.GET.get('status')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.select_related('employee', 'employee__user')

class AttendanceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Attendance
    permission_required = 'hr.view_attendance'
    template_name = 'hr/attendance_detail.html'
    context_object_name = 'attendance'

class AttendanceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Attendance
    permission_required = 'hr.change_attendance'
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث سجل الحضور بنجاح')
        return super().form_valid(form)

# Leave Views
class LeaveListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Leave
    permission_required = 'hr.view_leave'
    template_name = 'hr/leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        leave_type = self.request.GET.get('leave_type')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        if status:
            queryset = queryset.filter(status=status)
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)
            
        return queryset.select_related('employee', 'employee__user', 'approved_by')

class LeaveCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Leave
    permission_required = 'hr.add_leave'
    form_class = LeaveForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('hr:leave_list')

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee
        messages.success(self.request, 'تم تقديم طلب الإجازة بنجاح')
        return super().form_valid(form)

class LeaveDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Leave
    permission_required = 'hr.view_leave'
    template_name = 'hr/leave_detail.html'
    context_object_name = 'leave'

class LeaveUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Leave
    permission_required = 'hr.change_leave'
    form_class = LeaveForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('hr:leave_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث طلب الإجازة بنجاح')
        return super().form_valid(form)

class LeaveApproveView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Leave
    permission_required = 'hr.change_leave'
    template_name = 'hr/leave_approve.html'
    fields = ['approved_by', 'approved_at', 'status']
    success_url = reverse_lazy('hr:leave_list')

    def form_valid(self, form):
        form.instance.status = 'approved'
        form.instance.approved_by = self.request.user
        form.instance.approved_at = timezone.now()
        messages.success(self.request, 'تم الموافقة على طلب الإجازة')
        return super().form_valid(form)

class LeaveRejectView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Leave
    permission_required = 'hr.change_leave'
    template_name = 'hr/leave_reject.html'
    fields = ['rejection_reason', 'status']
    success_url = reverse_lazy('hr:leave_list')

    def form_valid(self, form):
        form.instance.status = 'rejected'
        form.instance.rejected_by = self.request.user
        form.instance.rejected_at = timezone.now()
        messages.success(self.request, 'تم رفض طلب الإجازة')
        return super().form_valid(form)

# Payroll Views
class PayrollListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Payroll
    permission_required = 'hr.view_payroll'
    template_name = 'hr/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        is_paid = self.request.GET.get('is_paid')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        if is_paid is not None:
            queryset = queryset.filter(is_paid=is_paid == 'true')
            
        return queryset.select_related('employee', 'employee__user', 'created_by')

class PayrollCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Payroll
    permission_required = 'hr.add_payroll'
    form_class = PayrollForm
    template_name = 'hr/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إنشاء كشف الراتب بنجاح')
        return super().form_valid(form)

class PayrollDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Payroll
    permission_required = 'hr.view_payroll'
    template_name = 'hr/payroll_detail.html'
    context_object_name = 'payroll'

class PayrollUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Payroll
    permission_required = 'hr.change_payroll'
    form_class = PayrollForm
    template_name = 'hr/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث كشف الراتب بنجاح')
        return super().form_valid(form)

class PayrollGenerateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Payroll
    permission_required = 'hr.add_payroll'
    form_class = PayrollForm
    template_name = 'hr/payroll_generate.html'
    success_url = reverse_lazy('hr:payroll_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء كشوف الرواتب بنجاح')
        return super().form_valid(form)

# Document Views
class DocumentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Document
    permission_required = 'hr.view_document'
    template_name = 'hr/document_list.html'
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        document_type = self.request.GET.get('document_type')
        is_verified = self.request.GET.get('is_verified')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified == 'true')
            
        return queryset.select_related('employee', 'employee__user', 'created_by')

class DocumentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Document
    permission_required = 'hr.add_document'
    form_class = DocumentForm
    template_name = 'hr/document_form.html'
    success_url = reverse_lazy('hr:document_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم رفع المستند بنجاح')
        return super().form_valid(form)

class DocumentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Document
    permission_required = 'hr.view_document'
    template_name = 'hr/document_detail.html'
    context_object_name = 'document'

class DocumentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Document
    permission_required = 'hr.change_document'
    form_class = DocumentForm
    template_name = 'hr/document_form.html'
    success_url = reverse_lazy('hr:document_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المستند بنجاح')
        return super().form_valid(form)
