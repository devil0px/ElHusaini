from rest_framework import serializers
from .models import Employee, Department, Position, Attendance, Leave, Payroll

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'middle_name', 'last_name',
            'national_id', 'birth_date', 'gender', 'nationality', 'marital_status',
            'photo', 'email', 'mobile', 'phone', 'address', 'emergency_contact',
            'department', 'department_name', 'position', 'position_title',
            'hire_date', 'employment_type', 'salary', 'bank_name', 'bank_account',
            'iban', 'id_copy', 'contract_copy', 'other_documents', 'notes',
            'is_active', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # إضافة معلومات إضافية إذا كانت مطلوبة
        return data

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'check_in',
            'check_out', 'status', 'notes', 'created_at', 'updated_at'
        ]

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    
    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'start_date',
            'end_date', 'reason', 'status', 'approved_by', 'approved_at',
            'rejected_by', 'rejected_at', 'rejection_reason', 'created_at',
            'updated_at'
        ]

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'month', 'year',
            'basic_salary', 'allowances', 'deductions', 'net_salary',
            'payment_date', 'payment_method', 'status', 'notes',
            'created_at', 'updated_at'
        ]
