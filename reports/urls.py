from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # الصفحة الرئيسية للتقارير
    path('', views.ReportListView.as_view(), name='report-list'),
    
    # التقارير المالية
    path('financial/', views.FinancialReportView.as_view(), name='financial-report'),
    path('financial/income/', views.IncomeReportView.as_view(), name='income-report'),
    path('financial/expenses/', views.ExpensesReportView.as_view(), name='expenses-report'),
    path('financial/profit-loss/', views.ProfitLossReportView.as_view(), name='profit-loss-report'),
    
    # تقارير المشاريع
    path('projects/', views.ProjectReportView.as_view(), name='project-report'),
    path('projects/status/', views.ProjectStatusReportView.as_view(), name='project-status-report'),
    path('projects/timeline/', views.ProjectTimelineReportView.as_view(), name='project-timeline-report'),
    path('projects/resources/', views.ProjectResourcesReportView.as_view(), name='project-resources-report'),
    
    # تقارير الموارد البشرية
    path('hr/', views.HRReportView.as_view(), name='hr-report'),
    path('hr/attendance/', views.AttendanceReportView.as_view(), name='attendance-report'),
    path('hr/leaves/', views.LeaveReportView.as_view(), name='leave-report'),
    path('hr/payroll/', views.PayrollReportView.as_view(), name='payroll-report'),
    
    # تقارير المخزون
    path('inventory/', views.InventoryReportView.as_view(), name='inventory-report'),
    path('inventory/stock/', views.StockReportView.as_view(), name='stock-report'),
    path('inventory/movement/', views.StockMovementReportView.as_view(), name='stock-movement-report'),
    path('inventory/valuation/', views.StockValuationReportView.as_view(), name='stock-valuation-report'),
    
    # تقارير العملاء
    path('clients/', views.ClientReportView.as_view(), name='client-report'),
    path('clients/contracts/', views.ClientContractsReportView.as_view(), name='client-contracts-report'),
    path('clients/payments/', views.ClientPaymentsReportView.as_view(), name='client-payments-report'),
    
    # لوحات المعلومات
    path('dashboard/overview/', views.DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('dashboard/projects/', views.ProjectsDashboardView.as_view(), name='projects-dashboard'),
    path('dashboard/financial/', views.FinancialDashboardView.as_view(), name='financial-dashboard'),
]
