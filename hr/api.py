from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Employee, Department, Position, Attendance, Leave, Payroll
from .serializers import (
    EmployeeSerializer, DepartmentSerializer, PositionSerializer,
    AttendanceSerializer, LeaveSerializer, PayrollSerializer
)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        department = self.request.query_params.get('department', '')
        position = self.request.query_params.get('position', '')
        status = self.request.query_params.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        if department:
            queryset = queryset.filter(department_id=department)
        
        if position:
            queryset = queryset.filter(position_id=position)
        
        if status:
            queryset = queryset.filter(is_active=status.lower() == 'active')
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()
        departments = Department.objects.count()
        positions = Position.objects.count()
        
        return Response({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'departments': departments,
            'positions': positions
        })

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        
        return queryset

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        department = self.request.query_params.get('department', '')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(code__icontains=search)
            )
        
        if department:
            queryset = queryset.filter(department_id=department)
        
        return queryset

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.query_params.get('employee', '')
        date_from = self.request.query_params.get('date_from', '')
        date_to = self.request.query_params.get('date_to', '')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.query_params.get('employee', '')
        status = self.request.query_params.get('status', '')
        date_from = self.request.query_params.get('date_from', '')
        date_to = self.request.query_params.get('date_to', '')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(end_date__lte=date_to)
        
        return queryset

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.query_params.get('employee', '')
        month = self.request.query_params.get('month', '')
        year = self.request.query_params.get('year', '')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        if month:
            queryset = queryset.filter(month=month)
        
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset
