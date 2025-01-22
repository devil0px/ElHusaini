from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

app_name = 'hr'

# إنشاء router للـ API
router = DefaultRouter()
router.register(r'employees', api.EmployeeViewSet, basename='api-employee')
router.register(r'departments', api.DepartmentViewSet)
router.register(r'positions', api.PositionViewSet)
router.register(r'attendance', api.AttendanceViewSet)
router.register(r'leaves', api.LeaveViewSet)
router.register(r'payroll', api.PayrollViewSet)

urlpatterns = [
    # مسارات API
    path('api/', include((router.urls, 'hr-api'))),
    
    # إدارة الموظفين
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # الحضور والانصراف
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendance/<int:pk>/update/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    
    # الإجازات
    path('leaves/', views.LeaveListView.as_view(), name='leave_list'),
    path('leaves/create/', views.LeaveCreateView.as_view(), name='leave_create'),
    path('leaves/<int:pk>/', views.LeaveDetailView.as_view(), name='leave_detail'),
    path('leaves/<int:pk>/update/', views.LeaveUpdateView.as_view(), name='leave_update'),
    path('leaves/<int:pk>/approve/', views.LeaveApproveView.as_view(), name='leave_approve'),
    path('leaves/<int:pk>/reject/', views.LeaveRejectView.as_view(), name='leave_reject'),
    
    # الرواتب
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    path('payroll/<int:pk>/update/', views.PayrollUpdateView.as_view(), name='payroll_update'),
    path('payroll/generate/', views.PayrollGenerateView.as_view(), name='payroll_generate'),
    
    # الأقسام
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    
    # الوظائف
    path('positions/', views.PositionListView.as_view(), name='position_list'),
    path('positions/create/', views.PositionCreateView.as_view(), name='position_create'),
    path('positions/<int:pk>/', views.PositionDetailView.as_view(), name='position_detail'),
    path('positions/<int:pk>/update/', views.PositionUpdateView.as_view(), name='position_update'),
]
