from datetime import datetime
from calendar import month_name
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg, F, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime, timedelta

from projects.models import Project
from hr.models import Employee, Attendance, Leave, Payroll
from inventory.models import Item, Stock, StockCount
from clients.models import Client
from contracts.models import Contract, ContractPayment
from core.models import Expense
from django.db.models import fields
from django.db.models.expressions import ExpressionWrapper

class BaseReportView(LoginRequiredMixin, TemplateView):
    def get_date_range(self):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if not start_date:
            start_date = timezone.now().date().replace(day=1)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = timezone.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        return start_date, end_date

class FinancialReportView(BaseReportView):
    template_name = 'reports/financial_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # إجمالي المدفوعات
        payments = ContractPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        )
        total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # إجمالي المصروفات
        expenses = 0  # يجب إضافة نموذج المصروفات
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_payments': total_payments,
            'total_expenses': expenses,
            'net_profit': total_payments - expenses
        })
        return context

class IncomeReportView(BaseReportView):
    template_name = 'reports/income_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        payments = ContractPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).order_by('payment_date')
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'payments': payments,
            'total_income': payments.aggregate(total=Sum('amount'))['total'] or 0
        })
        return context

class ExpensesReportView(BaseReportView):
    template_name = 'reports/expenses_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # يجب إضافة نموذج المصروفات
        expenses = []
        total_expenses = 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'expenses': expenses,
            'total_expenses': total_expenses
        })
        return context

class ProfitLossReportView(BaseReportView):
    template_name = 'reports/profit_loss_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الإيرادات
        income = ContractPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # المصروفات
        expenses = 0  # يجب إضافة نموذج المصروفات
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_income': income,
            'total_expenses': expenses,
            'net_profit': income - expenses
        })
        return context

class ProjectReportView(BaseReportView):
    template_name = 'reports/project_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # الحصول على جميع المشاريع
        projects = Project.objects.select_related('project_manager').all()
        
        # إحصائيات المشاريع
        total_projects = projects.count()
        active_projects = projects.filter(status='in_progress').count()
        delayed_projects = projects.filter(status='on_hold').count()
        completed_projects = projects.filter(status='completed').count()
        
        # إحصائيات حسب الحالة
        status_counts = {
            'planning': projects.filter(status='planning').count(),
            'in_progress': active_projects,
            'on_hold': delayed_projects,
            'completed': completed_projects,
            'cancelled': projects.filter(status='cancelled').count()
        }
        
        # بيانات تقدم المشاريع
        active_projects_list = projects.filter(status__in=['in_progress', 'on_hold'])
        project_names = [project.name for project in active_projects_list]
        # حساب نسبة الإنجاز من مراحل المشروع
        project_progress = []
        for project in active_projects_list:
            phases = project.phases.all()
            if phases:
                total_progress = sum(phase.completion_percentage for phase in phases)
                avg_progress = total_progress / phases.count()
                project_progress.append(float(avg_progress))
            else:
                project_progress.append(0)
        
        context.update({
            'projects': projects,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'delayed_projects': delayed_projects,
            'completed_projects': completed_projects,
            'status_counts': status_counts,
            'project_names': project_names,
            'project_progress': project_progress
        })
        return context

class ProjectStatusReportView(BaseReportView):
    template_name = 'reports/project_status_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على المشاريع في الفترة المحددة
        projects = Project.objects.filter(
            Q(start_date__range=[start_date, end_date]) |
            Q(end_date__range=[start_date, end_date]) |
            Q(start_date__lte=start_date, end_date__gte=end_date)
        ).select_related('project_manager', 'project_manager__employee', 'project_manager__employee__user').order_by('-start_date')
        
        # إحصائيات المشاريع
        total_projects = projects.count()
        completed_projects = projects.filter(status='completed').count()
        in_progress_projects = projects.filter(status='in_progress').count()
        delayed_projects = projects.filter(status='delayed').count()
        on_hold_projects = projects.filter(status='on_hold').count()
        
        # تجهيز بيانات الرسم البياني لنسبة الإنجاز
        project_data = []
        progress_colors = []
        progress_borders = []
        
        for project in projects:
            # حساب نسبة الإنجاز بناءً على المدة المنقضية
            if project.end_date and project.start_date:
                total_days = (project.end_date - project.start_date).days
                if total_days > 0:
                    days_passed = (timezone.now().date() - project.start_date).days
                    progress = min(100, max(0, (days_passed / total_days) * 100))
                else:
                    progress = 0
            else:
                progress = 0
            
            project_data.append({
                'name': project.name,
                'progress': progress
            })
            
            # تحديد لون شريط التقدم بناءً على نسبة الإنجاز
            if progress >= 75:
                color = '#28a745'
                border = '#1e7e34'
            elif progress >= 50:
                color = '#17a2b8'
                border = '#117a8b'
            elif progress >= 25:
                color = '#ffc107'
                border = '#d39e00'
            else:
                color = '#dc3545'
                border = '#bd2130'
            
            progress_colors.append(color)
            progress_borders.append(border)
        
        project_names = [p['name'] for p in project_data]
        project_progress = [p['progress'] for p in project_data]
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'projects': projects,
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'in_progress_projects': in_progress_projects,
            'delayed_projects': delayed_projects,
            'on_hold_projects': on_hold_projects,
            'completed_percentage': self.calculate_percentage(completed_projects, total_projects),
            'in_progress_percentage': self.calculate_percentage(in_progress_projects, total_projects),
            'delayed_percentage': self.calculate_percentage(delayed_projects, total_projects),
            'project_names': project_names,
            'project_progress': project_progress,
            'project_progress_colors': progress_colors,
            'project_progress_borders': progress_borders
        })
        return context
    
    def calculate_percentage(self, value, total):
        try:
            return round((value / total) * 100, 1)
        except ZeroDivisionError:
            return 0

class ProjectTimelineReportView(BaseReportView):
    template_name = 'reports/project_timeline_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على المشاريع في الفترة المحددة
        projects = Project.objects.filter(
            Q(start_date__range=[start_date, end_date]) |
            Q(end_date__range=[start_date, end_date]) |
            Q(start_date__lte=start_date, end_date__gte=end_date)
        ).select_related('project_manager', 'project_manager__employee', 'project_manager__employee__user').order_by('start_date')
        
        # حساب مدة كل مشروع
        for project in projects:
            if project.end_date and project.start_date:
                project.duration = (project.end_date - project.start_date).days
            else:
                project.duration = 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'projects': projects
        })
        return context

class ProjectResourcesReportView(BaseReportView):
    template_name = 'reports/project_resources_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على المشاريع في الفترة المحددة
        projects = Project.objects.filter(
            Q(start_date__range=[start_date, end_date]) |
            Q(end_date__range=[start_date, end_date]) |
            Q(start_date__lte=start_date, end_date__gte=end_date)
        ).select_related('project_manager').prefetch_related(
            'team_members',
            'projectteammember_set',
            'stock_transactions',
            'purchase_requests'
        ).order_by('start_date')
        
        # تجهيز إحصائيات لكل مشروع
        for project in projects:
            # إحصائيات الفريق
            project.team_count = project.team_members.count()
            project.total_hours = project.projectteammember_set.aggregate(
                total=Sum('hours_worked'))['total'] or 0
            project.labor_cost = project.projectteammember_set.aggregate(
                total=Sum('labor_cost'))['total'] or 0
            
            # إحصائيات المعدات والمواد
            stock_transactions = project.stock_transactions.all()
            project.equipment_count = stock_transactions.filter(
                item__type='equipment').count()
            project.equipment_cost = stock_transactions.filter(
                item__type='equipment').aggregate(
                total=Sum('total_cost'))['total'] or 0
            
            project.materials_count = stock_transactions.filter(
                item__type='material').count()
            project.materials_cost = stock_transactions.filter(
                item__type='material').aggregate(
                total=Sum('total_cost'))['total'] or 0
            
            project.total_resource_cost = (
                project.labor_cost +
                project.equipment_cost +
                project.materials_cost
            )
        
        # إحصائيات إجمالية
        total_projects = projects.count()
        total_employees = sum(p.team_count for p in projects)
        total_equipment = sum(p.equipment_count for p in projects)
        total_materials = sum(p.materials_count for p in projects)
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'projects': projects,
            'total_projects': total_projects,
            'total_employees': total_employees,
            'total_equipment': total_equipment,
            'total_materials': total_materials
        })
        return context

class HRReportView(BaseReportView):
    template_name = 'reports/hr_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        employees = Employee.objects.select_related('user').all()
        total_employees = employees.count()
        active_employees = employees.filter(user__is_active=True).count()
        
        # إحصائيات حسب نوع التوظيف
        employment_type_counts = {
            'full_time': employees.filter(employment_type='full_time').count(),
            'part_time': employees.filter(employment_type='part_time').count(),
            'contractor': employees.filter(employment_type='contractor').count(),
            'temporary': employees.filter(employment_type='temporary').count()
        }
        
        # إحصائيات الإجازات
        leaves = Leave.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )
        current_leaves = leaves.count()
        
        # إحصائيات الحضور لليوم
        today = timezone.now().date()
        attendance = Attendance.objects.filter(date=today)
        present_today = attendance.filter(status='present').count()
        absent_today = attendance.filter(status='absent').count()
        late_today = attendance.filter(status='late').count()
        
        context.update({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'employment_type_counts': employment_type_counts,
            'current_leaves': current_leaves,
            'present_today': present_today,
            'absent_today': absent_today,
            'late_today': late_today
        })
        return context

class AttendanceReportView(BaseReportView):
    template_name = 'reports/attendance_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على سجلات الحضور في الفترة المحددة
        attendance_records = Attendance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('employee', 'employee__user').order_by('-date', '-time_in')
        
        # إحصائيات الحضور
        total_records = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        late_count = attendance_records.filter(status='late').count()
        leave_count = attendance_records.filter(status__in=['vacation', 'sick_leave']).count()
        
        attendance_stats = {
            'present': present_count,
            'absent': absent_count,
            'late': late_count,
            'on_leave': leave_count,
            'present_percentage': self.calculate_percentage(present_count, total_records),
            'absent_percentage': self.calculate_percentage(absent_count, total_records),
            'late_percentage': self.calculate_percentage(late_count, total_records),
            'leave_percentage': self.calculate_percentage(leave_count, total_records)
        }
        
        # بيانات الرسم البياني اليومي
        daily_stats = {}
        current_date = start_date
        while current_date <= end_date:
            daily_records = attendance_records.filter(date=current_date)
            daily_stats[current_date.strftime('%Y-%m-%d')] = {
                'present': daily_records.filter(status='present').count(),
                'absent': daily_records.filter(status='absent').count(),
                'late': daily_records.filter(status='late').count()
            }
            current_date += timedelta(days=1)
        
        daily_labels = list(daily_stats.keys())
        daily_present = [stats['present'] for stats in daily_stats.values()]
        daily_absent = [stats['absent'] for stats in daily_stats.values()]
        daily_late = [stats['late'] for stats in daily_stats.values()]
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'attendance_records': attendance_records,
            'attendance_stats': attendance_stats,
            'daily_labels': daily_labels,
            'daily_present': daily_present,
            'daily_absent': daily_absent,
            'daily_late': daily_late
        })
        return context
    
    def calculate_percentage(self, value, total):
        try:
            return round((value / total) * 100, 1)
        except ZeroDivisionError:
            return 0

class LeaveReportView(BaseReportView):
    template_name = 'reports/leave_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على الإجازات في الفترة المحددة
        leaves = Leave.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('employee', 'employee__user', 'approved_by').order_by('-start_date')
        
        # إحصائيات الإجازات
        total_leaves = leaves.count()
        approved_leaves = leaves.filter(status='approved').count()
        pending_leaves = leaves.filter(status='pending').count()
        rejected_leaves = leaves.filter(status='rejected').count()
        cancelled_leaves = leaves.filter(status='cancelled').count()
        
        # إحصائيات أنواع الإجازات
        leave_type_stats = {
            'annual': leaves.filter(leave_type='annual').count(),
            'sick': leaves.filter(leave_type='sick').count(),
            'unpaid': leaves.filter(leave_type='unpaid').count(),
            'emergency': leaves.filter(leave_type='emergency').count(),
            'other': leaves.filter(leave_type='other').count()
        }
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'leaves': leaves,
            'total_leaves': total_leaves,
            'approved_leaves': approved_leaves,
            'pending_leaves': pending_leaves,
            'rejected_leaves': rejected_leaves,
            'cancelled_leaves': cancelled_leaves,
            'approved_percentage': self.calculate_percentage(approved_leaves, total_leaves),
            'pending_percentage': self.calculate_percentage(pending_leaves, total_leaves),
            'rejected_percentage': self.calculate_percentage(rejected_leaves, total_leaves),
            'leave_type_stats': leave_type_stats
        })
        return context
    
    def calculate_percentage(self, value, total):
        try:
            return round((value / total) * 100, 1)
        except ZeroDivisionError:
            return 0

class PayrollReportView(BaseReportView):
    template_name = 'reports/payroll_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على كشوف المرتبات في الفترة المحددة
        payrolls = Payroll.objects.filter(
            year__range=[start_date.year, end_date.year],
            month__range=[start_date.month, end_date.month]
        ).select_related('employee', 'employee__user').order_by('-year', '-month')
        
        # إحصائيات المرتبات
        total_payrolls = payrolls.count()
        total_salaries = payrolls.aggregate(total=Sum('net_salary'))['total'] or 0
        total_deductions = payrolls.aggregate(total=Sum('deductions'))['total'] or 0
        total_bonuses = payrolls.aggregate(
            total=Sum('bonuses') + Sum('overtime')
        )['total'] or 0
        
        # إحصائيات حسب الشهر
        monthly_stats = {}
        current_date = start_date
        while current_date <= end_date:
            month_payrolls = payrolls.filter(year=current_date.year, month=current_date.month)
            monthly_stats[current_date.strftime('%Y-%m')] = {
                'count': month_payrolls.count(),
                'total': month_payrolls.aggregate(total=Sum('net_salary'))['total'] or 0,
                'deductions': month_payrolls.aggregate(total=Sum('deductions'))['total'] or 0,
                'bonuses': month_payrolls.aggregate(
                    total=Sum('bonuses') + Sum('overtime')
                )['total'] or 0
            }
            # الانتقال للشهر التالي
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # تجهيز بيانات الرسم البياني
        monthly_labels = list(monthly_stats.keys())
        monthly_totals = [stats['total'] for stats in monthly_stats.values()]
        monthly_deductions = [stats['deductions'] for stats in monthly_stats.values()]
        monthly_bonuses = [stats['bonuses'] for stats in monthly_stats.values()]
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'payrolls': payrolls,
            'total_payrolls': total_payrolls,
            'total_salaries': total_salaries,
            'total_deductions': total_deductions,
            'total_bonuses': total_bonuses,
            'monthly_labels': monthly_labels,
            'monthly_totals': monthly_totals,
            'monthly_deductions': monthly_deductions,
            'monthly_bonuses': monthly_bonuses,
            'average_salary': total_salaries / total_payrolls if total_payrolls > 0 else 0
        })
        return context

class InventoryReportView(BaseReportView):
    template_name = 'reports/inventory_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        item_type = self.request.GET.get('item_type', '')
        
        # فلتر العناصر حسب النوع
        items_filter = {}
        if item_type:
            items_filter['type'] = item_type
        
        # الحصول على العناصر وحركات المخزون
        items = Item.objects.filter(**items_filter)
        transactions = Stock.objects.filter(
            created_at__range=[start_date, end_date],
            item__in=items
        ).select_related('item', 'project').order_by('-created_at')
        
        # حساب متوسط الاستهلاك الشهري لكل عنصر
        for item in items:
            # حساب الكمية المستهلكة في الفترة
            consumption = transactions.filter(
                item=item,
                transaction_type='out'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            # حساب عدد الأشهر في الفترة
            months = (end_date - start_date).days / 30
            if months > 0:
                item.monthly_consumption = consumption / months
            else:
                item.monthly_consumption = 0
            
            # حساب القيمة الحالية
            item.current_value = item.quantity * item.purchase_price if hasattr(item, 'quantity') else 0
        
        # إحصائيات المخزون
        total_items = items.count()
        total_value = sum(item.current_value for item in items)
        low_stock_items = sum(1 for item in items if hasattr(item, 'quantity') and 0 < item.quantity <= item.minimum_quantity)
        out_of_stock_items = sum(1 for item in items if hasattr(item, 'quantity') and item.quantity == 0)
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'item_type': item_type,
            'items': items,
            'transactions': transactions,
            'total_items': total_items,
            'total_value': total_value,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items
        })
        return context

class StockReportView(BaseReportView):
    template_name = 'reports/stock_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # الحصول على عمليات الجرد في الفترة المحددة
        stock_counts = StockCount.objects.filter(
            count_date__range=[start_date, end_date]
        ).select_related('item', 'counted_by').order_by('-count_date')
        
        # حساب النسبة المئوية للفرق لكل عملية جرد
        for count in stock_counts:
            if count.system_quantity:
                count.difference_percentage = (count.difference / count.system_quantity) * 100
            else:
                count.difference_percentage = 0
        
        # إحصائيات الجرد
        total_counts = stock_counts.count()
        matching_items = stock_counts.filter(difference=0).count()
        surplus_items = stock_counts.filter(difference__gt=0).count()
        shortage_items = stock_counts.filter(difference__lt=0).count()
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'stock_counts': stock_counts,
            'total_counts': total_counts,
            'matching_items': matching_items,
            'surplus_items': surplus_items,
            'shortage_items': shortage_items
        })
        return context

class StockMovementReportView(BaseReportView):
    template_name = 'reports/stock_movement_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        movements = Stock.objects.filter(
            created_at__range=[start_date, end_date]
        ).order_by('created_at', 'item')
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'movements': movements
        })
        return context

class StockValuationReportView(BaseReportView):
    template_name = 'reports/stock_valuation_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        items = Item.objects.all()
        total_value = 0
        
        for item in items:
            stock_in = Stock.objects.filter(
                item=item,
                transaction_type='in'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            stock_out = Stock.objects.filter(
                item=item,
                transaction_type='out'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            item.current_stock = stock_in - stock_out
            item.total_value = item.current_stock * item.purchase_price
            total_value += item.total_value
        
        context.update({
            'items': items,
            'total_value': total_value
        })
        return context

class ValuationReportView(BaseReportView):
    template_name = 'reports/stock_valuation_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item_type = self.request.GET.get('item_type', '')
        
        # فلترة الأصناف
        items = Item.objects.all()
        if item_type:
            items = items.filter(type=item_type)
        
        # حساب القيم لكل صنف
        for item in items:
            # حساب متوسط سعر الوحدة من آخر عمليات الشراء
            recent_purchases = Stock.objects.filter(
                item=item,
                transaction_type='in'
            ).order_by('-created_at')[:5]  # آخر 5 عمليات شراء
            
            if recent_purchases:
                avg_unit_price = sum(p.unit_price for p in recent_purchases) / len(recent_purchases)
            else:
                avg_unit_price = 0
                
            item.average_unit_price = avg_unit_price
            item.total_value = item.quantity * avg_unit_price
        
        # إحصائيات عامة
        total_items = items.count()
        total_quantity = sum(item.quantity for item in items)
        total_value = sum(item.total_value for item in items)
        average_value = total_value / total_items if total_items > 0 else 0
        
        # تحليل حسب التصنيف
        type_analysis = []
        for type_choice in Item.TYPE_CHOICES:
            type_items = [item for item in items if item.type == type_choice[0]]
            if type_items:
                type_analysis.append({
                    'type': type_choice[0],
                    'type_display': type_choice[1],
                    'total_quantity': sum(item.quantity for item in type_items),
                    'total_value': sum(item.total_value for item in type_items)
                })
        
        context.update({
            'items': items,
            'item_type': item_type,
            'item_types': Item.TYPE_CHOICES,
            'total_items': total_items,
            'total_quantity': total_quantity,
            'total_value': total_value,
            'average_value': average_value,
            'type_analysis': type_analysis
        })
        return context

class ClientReportView(BaseReportView):
    template_name = 'reports/client_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_type = self.request.GET.get('client_type', '')
        
        # فلترة العملاء
        clients = Client.objects.all()
        if client_type:
            clients = clients.filter(client_type=client_type)
        
        # إحصائيات العملاء
        total_clients = clients.count()
        
        # حساب إحصائيات كل عميل
        for client in clients:
            client.projects_count = Project.objects.filter(client=client).count()
            
            contracts = Contract.objects.filter(project__client=client)
            client.total_contract_value = contracts.aggregate(total=Sum('total_value'))['total'] or 0
            
            payments = ContractPayment.objects.filter(contract__project__client=client)
            client.total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
            client.total_due = client.total_contract_value - client.total_payments
            
            active_contracts = contracts.filter(status='active').count()
            client.has_active_contracts = active_contracts > 0
        
        # إحصائيات عامة
        active_clients = sum(1 for client in clients if client.has_active_contracts)
        total_projects = sum(client.projects_count for client in clients)
        total_contract_value = sum(client.total_contract_value for client in clients)
        
        # تحليل توزيع العملاء حسب النوع
        client_types = []
        for type_choice in Client.CLIENT_TYPE_CHOICES:
            count = clients.filter(client_type=type_choice[0]).count()
            if count > 0:
                client_types.append({
                    'type': type_choice[0],
                    'type_display': type_choice[1],
                    'count': count,
                    'percentage': (count / total_clients * 100) if total_clients > 0 else 0
                })
        
        # أفضل 5 عملاء من حيث قيمة العقود
        top_clients = sorted(
            clients,
            key=lambda x: x.total_contract_value,
            reverse=True
        )[:5]
        
        context.update({
            'clients': clients,
            'client_type': client_type,
            'client_types': client_types,
            'total_clients': total_clients,
            'active_clients': active_clients,
            'total_projects': total_projects,
            'total_contract_value': total_contract_value,
            'top_clients': top_clients
        })
        return context

class ClientContractsReportView(BaseReportView):
    template_name = 'reports/client_contracts_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        status = self.request.GET.get('status', '')
        
        # فلترة العقود
        contracts = Contract.objects.select_related(
            'project',
            'project__project_manager'
        ).order_by('-signing_date')
        
        if start_date and end_date:
            contracts = contracts.filter(signing_date__range=[start_date, end_date])
        
        if status:
            contracts = contracts.filter(status=status)
            
        # حساب المدفوعات والمتبقي لكل عقد
        for contract in contracts:
            payments = ContractPayment.objects.filter(contract=contract)
            contract.total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
            contract.remaining_amount = contract.total_value - contract.total_payments
            
            # حساب نسبة الإنجاز
            if contract.status == 'completed':
                contract.completion_percentage = 100
            else:
                total_days = (contract.end_date - contract.start_date).days
                if total_days > 0:
                    days_passed = (timezone.now().date() - contract.start_date).days
                    contract.completion_percentage = min(100, max(0, (days_passed / total_days) * 100))
                else:
                    contract.completion_percentage = 0
        
        # إحصائيات عامة
        total_contracts = contracts.count()
        total_amount = sum(contract.total_value for contract in contracts)
        total_payments = sum(contract.total_payments for contract in contracts)
        total_remaining = total_amount - total_payments
        
        # تحليل توزيع العقود حسب الحالة
        status_distribution = []
        for status_choice in Contract.STATUS_CHOICES:
            count = len([contract for contract in contracts if contract.status == status_choice[0]])
            if count > 0:
                status_distribution.append({
                    'status': status_choice[0],
                    'status_display': status_choice[1],
                    'count': count,
                    'percentage': (count / total_contracts * 100) if total_contracts > 0 else 0
                })
        
        # تحليل المدفوعات الشهرية
        monthly_payments = []
        if contracts:
            payments = ContractPayment.objects.filter(
                contract__in=contracts,
                payment_date__range=[start_date, end_date]
            ).order_by('payment_date')
            
            if payments:
                current_month = payments.first().payment_date.replace(day=1)
                last_month = payments.last().payment_date.replace(day=1)
                
                while current_month <= last_month:
                    month_payments = payments.filter(
                        payment_date__year=current_month.year,
                        payment_date__month=current_month.month
                    )
                    
                    monthly_payments.append({
                        'month_name': f"{month_name[current_month.month]} {current_month.year}",
                        'total_amount': month_payments.aggregate(total=Sum('amount'))['total'] or 0
                    })
                    
                    if current_month.month == 12:
                        current_month = current_month.replace(year=current_month.year + 1, month=1)
                    else:
                        current_month = current_month.replace(month=current_month.month + 1)
        
        context.update({
            'contracts': contracts,
            'start_date': start_date,
            'end_date': end_date,
            'total_contracts': total_contracts,
            'total_amount': total_amount,
            'total_payments': total_payments,
            'total_remaining': total_remaining,
            'status_distribution': status_distribution,
            'monthly_payments': monthly_payments
        })
        return context

class ClientPaymentsReportView(BaseReportView):
    template_name = 'reports/client_payments_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        client_id = self.request.GET.get('client', '')
        
        # فلترة المدفوعات
        payments = ContractPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).select_related(
            'contract',
            'contract__project'
        ).order_by('-payment_date')
        
        if client_id:
            payments = payments.filter(contract__project__client_id=client_id)
        
        # إحصائيات المدفوعات
        payments_count = payments.count()
        total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # حساب إجمالي المستحقات
        contracts_filter = {}
        if client_id:
            contracts_filter['project__client_id'] = client_id
            
        contracts = Contract.objects.filter(**contracts_filter)
        total_contracts_value = contracts.aggregate(total=Sum('total_value'))['total'] or 0
        total_due = total_contracts_value - total_payments
        
        # حساب نسبة التحصيل
        collection_percentage = (total_payments / total_contracts_value * 100) if total_contracts_value > 0 else 0
        
        # المدفوعات المتأخرة
        today = timezone.now().date()
        overdue_payments = ContractPayment.objects.filter(
            status='pending',
            due_date__lt=today
        ).select_related(
            'contract',
            'contract__project',
            'contract__project__client'
        )
        
        for payment in overdue_payments:
            payment.days_overdue = (today - payment.due_date).days
        
        # تحليل المدفوعات الشهرية
        monthly_payments = []
        if payments:
            current_month = payments.order_by('payment_date').first().payment_date.replace(day=1)
            last_month = payments.order_by('-payment_date').first().payment_date.replace(day=1)
            
            while current_month <= last_month:
                month_payments = payments.filter(
                    payment_date__year=current_month.year,
                    payment_date__month=current_month.month
                )
                
                monthly_payments.append({
                    'month_name': f"{month_name[current_month.month]} {current_month.year}",
                    'total_amount': month_payments.aggregate(total=Sum('amount'))['total'] or 0
                })
                
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
        
        # تحليل طرق الدفع
        payment_methods = []
        for method_choice in ContractPayment.PAYMENT_TYPE_CHOICES:
            count = payments.filter(payment_type=method_choice[0]).count()
            if count > 0:
                payment_methods.append({
                    'method': method_choice[0],
                    'method_display': method_choice[1],
                    'count': count
                })
        
        # ملخص العملاء
        client_summaries = []
        clients_filter = {}
        if client_id:
            clients_filter['id'] = client_id
            
        clients = Client.objects.filter(**clients_filter)
            
        for client in clients:
            client_contracts = Contract.objects.filter(project__client=client)
            client_payments = ContractPayment.objects.filter(
                contract__project__client=client,
                payment_date__range=[start_date, end_date]
            )
            
            total_contracts = client_contracts.aggregate(total=Sum('total_value'))['total'] or 0
            total_client_payments = client_payments.aggregate(total=Sum('amount'))['total'] or 0
            
            if total_contracts > 0:
                client_summaries.append({
                    'name': client.name,
                    'total_contracts': total_contracts,
                    'total_payments': total_client_payments,
                    'total_due': total_contracts - total_client_payments,
                    'collection_percentage': (total_client_payments / total_contracts * 100) if total_contracts > 0 else 0
                })
        
        context.update({
            'payments': payments,
            'client_id': client_id,
            'clients_list': Client.objects.all(),
            'payments_count': payments_count,
            'total_payments': total_payments,
            'total_due': total_due,
            'collection_percentage': collection_percentage,
            'monthly_payments': monthly_payments,
            'payment_methods': payment_methods,
            'client_summaries': client_summaries,
            'start_date': start_date,
            'end_date': end_date
        })
        return context

class DashboardOverviewView(BaseReportView):
    template_name = 'reports/dashboard_overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        today = timezone.now().date()
        
        # المشاريع النشطة
        active_projects = Project.objects.filter(
            status='active'
        ).select_related('project_manager')
        
        active_projects_count = active_projects.count()
        total_completion = 0
        delayed_projects = []
        
        for project in active_projects:
            # حساب نسبة الإنجاز
            if project.status == 'completed':
                project.completion_percentage = 100
            else:
                total_days = (project.end_date - project.start_date).days
                if total_days > 0:
                    days_passed = (today - project.start_date).days
                    project.completion_percentage = min(100, max(0, (days_passed / total_days) * 100))
                else:
                    project.completion_percentage = 0
            
            total_completion += project.completion_percentage
            
            # تحديد المشاريع المتأخرة
            if project.end_date < today:
                project.days_delayed = (today - project.end_date).days
                delayed_projects.append(project)
        
        projects_completion_rate = total_completion / active_projects_count if active_projects_count > 0 else 0
        
        # العقود الجديدة
        new_contracts = Contract.objects.filter(
            signing_date__range=[start_date, end_date]
        )
        new_contracts_count = new_contracts.count()
        new_contracts_value = new_contracts.aggregate(total=Sum('total_value'))['total'] or 0
        
        # المدفوعات
        payments = ContractPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).select_related(
            'contract',
            'contract__project',
            'contract__project__project_manager'
        )
        payments_count = payments.count()
        total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # المدفوعات المتأخرة
        overdue_payments = ContractPayment.objects.filter(
            status='pending',
            due_date__lt=today
        ).select_related(
            'contract',
            'contract__project',
            'contract__project__project_manager'
        )
        
        for payment in overdue_payments:
            payment.days_overdue = (today - payment.due_date).days
        
        # المصروفات
        expenses = Expense.objects.filter(date__range=[start_date, end_date])
        expenses_count = expenses.count()
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        # تحليل المدفوعات الشهرية
        monthly_payments = []
        if payments:
            current_month = payments.order_by('payment_date').first().payment_date.replace(day=1)
            last_month = payments.order_by('-payment_date').first().payment_date.replace(day=1)
            
            while current_month <= last_month:
                month_payments = payments.filter(
                    payment_date__year=current_month.year,
                    payment_date__month=current_month.month
                )
                
                monthly_payments.append({
                    'month_name': f"{month_name[current_month.month]} {current_month.year}",
                    'total_amount': month_payments.aggregate(total=Sum('amount'))['total'] or 0
                })
                
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
        
        # تحليل المصروفات الشهرية
        monthly_expenses = []
        if expenses:
            current_month = expenses.order_by('date').first().date.replace(day=1)
            last_month = expenses.order_by('-date').first().date.replace(day=1)
            
            while current_month <= last_month:
                month_expenses = expenses.filter(
                    date__year=current_month.year,
                    date__month=current_month.month
                )
                
                monthly_expenses.append({
                    'month_name': f"{month_name[current_month.month]} {current_month.year}",
                    'total_amount': month_expenses.aggregate(total=Sum('amount'))['total'] or 0
                })
                
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
        
        # توزيع حالة المشاريع
        all_projects = Project.objects.all()
        project_status_distribution = []
        for status_choice in Project.STATUS_CHOICES:
            count = all_projects.filter(status=status_choice[0]).count()
            if count > 0:
                project_status_distribution.append({
                    'status': status_choice[0],
                    'status_display': status_choice[1],
                    'count': count
                })
        
        # توزيع حالة العقود
        all_contracts = Contract.objects.all()
        contract_status_distribution = []
        for status_choice in Contract.STATUS_CHOICES:
            count = all_contracts.filter(status=status_choice[0]).count()
            if count > 0:
                contract_status_distribution.append({
                    'status': status_choice[0],
                    'status_display': status_choice[1],
                    'count': count
                })
        
        context.update({
            'active_projects_count': active_projects_count,
            'projects_completion_rate': projects_completion_rate,
            'new_contracts_count': new_contracts_count,
            'new_contracts_value': new_contracts_value,
            'payments_count': payments_count,
            'total_payments': total_payments,
            'expenses_count': expenses_count,
            'total_expenses': total_expenses,
            'delayed_projects': delayed_projects,
            'overdue_payments': overdue_payments,
            'monthly_payments': monthly_payments,
            'monthly_expenses': monthly_expenses,
            'project_status_distribution': project_status_distribution,
            'contract_status_distribution': contract_status_distribution,
            'start_date': start_date,
            'end_date': end_date
        })
        return context

class ProjectsDashboardView(BaseReportView):
    template_name = 'reports/projects_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        projects = Project.objects.all()
        
        # المشاريع حسب الحالة
        status_counts = projects.values('status').annotate(count=Count('id'))
        
        # المشاريع المتأخرة
        overdue_projects = projects.filter(
            end_date__lt=timezone.now().date(),
            status__in=['new', 'in_progress']
        )
        
        # المشاريع القادمة
        upcoming_projects = projects.filter(
            start_date__gt=timezone.now().date()
        )
        
        context.update({
            'status_counts': status_counts,
            'overdue_projects': overdue_projects,
            'upcoming_projects': upcoming_projects
        })
        return context

class FinancialDashboardView(BaseReportView):
    template_name = 'reports/financial_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # العقود النشطة
        active_contracts = Contract.objects.filter(
            status='active'
        ).select_related(
            'project',
            'project__project_manager'
        )
        
        # حساب المدفوعات لكل عقد
        for contract in active_contracts:
            payments = ContractPayment.objects.filter(contract=contract)
            contract.total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
            contract.remaining_amount = contract.total_value - contract.total_payments
            contract.collection_percentage = (contract.total_payments / contract.total_value * 100) if contract.total_value > 0 else 0
        
        # إحصائيات العقود
        contracts_count = active_contracts.count()
        total_contracts_value = active_contracts.aggregate(total=Sum('total_value'))['total'] or 0
        
        # المدفوعات
        start_date = timezone.now().date().replace(day=1)
        end_date = timezone.now().date()
        
        payments = ContractPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).select_related(
            'contract',
            'contract__project',
            'contract__project__project_manager'
        )
        payments_count = payments.count()
        total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # المستحقات والتحصيل
        total_due = total_contracts_value - total_payments
        collection_percentage = (total_payments / total_contracts_value * 100) if total_contracts_value > 0 else 0
        
        # المدفوعات المتأخرة
        today = timezone.now().date()
        overdue_payments = ContractPayment.objects.filter(
            status='pending',
            due_date__lt=today
        ).select_related(
            'contract',
            'contract__project',
            'contract__project__project_manager'
        )
        
        for payment in overdue_payments:
            payment.days_overdue = (today - payment.due_date).days
        
        # تحليل المدفوعات الشهرية
        monthly_payments = []
        if payments:
            current_month = payments.order_by('payment_date').first().payment_date.replace(day=1)
            last_month = payments.order_by('-payment_date').first().payment_date.replace(day=1)
            
            while current_month <= last_month:
                month_payments = payments.filter(
                    payment_date__year=current_month.year,
                    payment_date__month=current_month.month
                )
                
                monthly_payments.append({
                    'month_name': f"{month_name[current_month.month]} {current_month.year}",
                    'total_amount': month_payments.aggregate(total=Sum('amount'))['total'] or 0
                })
                
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
        
        # تحليل المصروفات الشهرية
        monthly_expenses = []
        expenses = Expense.objects.filter(date__range=[start_date, end_date])
        expenses_count = expenses.count()
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        if expenses:
            current_month = expenses.order_by('date').first().date.replace(day=1)
            last_month = expenses.order_by('-date').first().date.replace(day=1)
            
            while current_month <= last_month:
                month_expenses = expenses.filter(
                    date__year=current_month.year,
                    date__month=current_month.month
                )
                
                monthly_expenses.append({
                    'month_name': f"{month_name[current_month.month]} {current_month.year}",
                    'total_amount': month_expenses.aggregate(total=Sum('amount'))['total'] or 0
                })
                
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
        
        context.update({
            'active_contracts': active_contracts,
            'contracts_count': contracts_count,
            'total_contracts_value': total_contracts_value,
            'payments_count': payments_count,
            'total_payments': total_payments,
            'total_due': total_due,
            'collection_percentage': collection_percentage,
            'expenses_count': expenses_count,
            'total_expenses': total_expenses,
            'overdue_payments': overdue_payments,
            'monthly_payments': monthly_payments,
            'monthly_expenses': monthly_expenses
        })
        return context

class ReportListView(BaseReportView):
    template_name = 'reports/report_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reports = [
            {
                'title': 'التقارير المالية',
                'icon': 'fas fa-money-bill-wave',
                'color': 'primary',
                'reports': [
                    {'name': 'التقرير المالي العام', 'url': 'reports:financial-report'},
                    {'name': 'تقرير الإيرادات', 'url': 'reports:income-report'},
                    {'name': 'تقرير المصروفات', 'url': 'reports:expenses-report'},
                    {'name': 'تقرير الأرباح والخسائر', 'url': 'reports:profit-loss-report'},
                ]
            },
            {
                'title': 'تقارير المشاريع',
                'icon': 'fas fa-project-diagram',
                'color': 'success',
                'reports': [
                    {'name': 'تقرير المشاريع', 'url': 'reports:project-report'},
                    {'name': 'تقرير حالة المشاريع', 'url': 'reports:project-status-report'},
                    {'name': 'تقرير جدول المشاريع', 'url': 'reports:project-timeline-report'},
                    {'name': 'تقرير موارد المشاريع', 'url': 'reports:project-resources-report'},
                ]
            },
            {
                'title': 'تقارير الموارد البشرية',
                'icon': 'fas fa-users',
                'color': 'info',
                'reports': [
                    {'name': 'تقرير الموارد البشرية', 'url': 'reports:hr-report'},
                    {'name': 'تقرير الحضور', 'url': 'reports:attendance-report'},
                    {'name': 'تقرير الإجازات', 'url': 'reports:leave-report'},
                    {'name': 'تقرير الرواتب', 'url': 'reports:payroll-report'},
                ]
            },
            {
                'title': 'تقارير المخزون',
                'icon': 'fas fa-boxes',
                'color': 'warning',
                'reports': [
                    {'name': 'تقرير المخزون', 'url': 'reports:inventory-report'},
                    {'name': 'تقرير المخزون الحالي', 'url': 'reports:stock-report'},
                    {'name': 'تقرير حركة المخزون', 'url': 'reports:stock-movement-report'},
                    {'name': 'تقرير تقييم المخزون', 'url': 'reports:stock-valuation-report'},
                ]
            },
            {
                'title': 'تقارير العملاء',
                'icon': 'fas fa-users-cog',
                'color': 'danger',
                'reports': [
                    {'name': 'تقرير العملاء', 'url': 'reports:client-report'},
                    {'name': 'تقرير عقود العملاء', 'url': 'reports:client-contracts-report'},
                    {'name': 'تقرير مدفوعات العملاء', 'url': 'reports:client-payments-report'},
                ]
            },
            {
                'title': 'لوحات المعلومات',
                'icon': 'fas fa-chart-bar',
                'color': 'secondary',
                'reports': [
                    {'name': 'نظرة عامة', 'url': 'reports:dashboard-overview'},
                    {'name': 'لوحة المشاريع', 'url': 'reports:projects-dashboard'},
                    {'name': 'لوحة المالية', 'url': 'reports:financial-dashboard'},
                ]
            },
        ]
        context['reports'] = reports
        return context

class MovementReportView(BaseReportView):
    template_name = 'reports/stock_movement_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        transaction_type = self.request.GET.get('transaction_type', '')
        
        # فلترة حركات المخزون
        movements = Stock.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('item', 'project', 'supplier', 'created_by')
        
        if transaction_type:
            movements = movements.filter(transaction_type=transaction_type)
            
        movements = movements.order_by('-created_at')
        
        # إحصائيات الحركات
        total_movements = movements.count()
        total_in = movements.filter(transaction_type='in').count()
        total_out = movements.filter(transaction_type='out').count()
        total_value = movements.aggregate(total=Sum('total_price'))['total'] or 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'transaction_type': transaction_type,
            'movements': movements,
            'total_movements': total_movements,
            'total_in': total_in,
            'total_out': total_out,
            'total_value': total_value
        })
        return context

class ProjectsDashboardView(BaseReportView):
    template_name = 'reports/projects_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_date_range()
        
        # جميع المشاريع
        projects = Project.objects.select_related('project_manager')
        if start_date and end_date:
            projects = projects.filter(start_date__range=[start_date, end_date])
        
        # إحصائيات المشاريع
        total_projects = projects.count()
        active_projects = projects.filter(status='active')
        active_projects_count = active_projects.count()
        
        # حساب متوسط مدة المشروع
        completed_projects = projects.filter(status='completed')
        if completed_projects:
            avg_duration = completed_projects.annotate(
                duration=ExpressionWrapper(
                    F('end_date') - F('start_date'),
                    output_field=fields.DurationField()
                )
            ).aggregate(avg=Avg('duration'))['avg']
            avg_project_duration = avg_duration.days if avg_duration else 0
        else:
            avg_project_duration = 0
        
        # حساب نسبة الإنجاز والمشاريع المتأخرة
        today = timezone.now().date()
        delayed_projects = []
        total_completion = 0
        
        for project in active_projects:
            # حساب نسبة الإنجاز
            if project.status == 'completed':
                project.completion_percentage = 100
            else:
                total_days = (project.end_date - project.start_date).days
                if total_days > 0:
                    days_passed = (today - project.start_date).days
                    project.completion_percentage = min(100, max(0, (days_passed / total_days) * 100))
                else:
                    project.completion_percentage = 0
            
            total_completion += project.completion_percentage
            
            # تحديد المشاريع المتأخرة
            if project.end_date < today:
                project.is_delayed = True
                project.days_delayed = (today - project.end_date).days
                delayed_projects.append(project)
            else:
                project.is_delayed = False
        
        completion_rate = total_completion / active_projects_count if active_projects_count > 0 else 0
        delayed_projects_count = len(delayed_projects)
        delayed_percentage = (delayed_projects_count / active_projects_count * 100) if active_projects_count > 0 else 0
        
        # توزيع حالة المشاريع
        project_status_distribution = []
        for status_choice in Project.STATUS_CHOICES:
            count = projects.filter(status=status_choice[0]).count()
            if count > 0:
                project_status_distribution.append({
                    'status': status_choice[0],
                    'status_display': status_choice[1],
                    'count': count,
                    'percentage': (count / total_projects * 100) if total_projects > 0 else 0
                })
        
        # توزيع المشاريع حسب المدير
        project_manager_distribution = []
        project_managers = User.objects.filter(
            id__in=projects.values_list('project_manager', flat=True).distinct()
        )
        
        for manager in project_managers:
            count = projects.filter(project_manager=manager).count()
            if count > 0:
                project_manager_distribution.append({
                    'name': manager.get_full_name() or manager.username,
                    'count': count,
                    'percentage': (count / total_projects * 100) if total_projects > 0 else 0
                })
        
        context.update({
            'total_projects': total_projects,
            'active_projects': active_projects,
            'active_projects_count': active_projects_count,
            'avg_project_duration': avg_project_duration,
            'completion_rate': completion_rate,
            'delayed_projects': delayed_projects,
            'delayed_projects_count': delayed_projects_count,
            'delayed_percentage': delayed_percentage,
            'project_status_distribution': project_status_distribution,
            'project_manager_distribution': project_manager_distribution,
            'start_date': start_date,
            'end_date': end_date
        })
        return context
