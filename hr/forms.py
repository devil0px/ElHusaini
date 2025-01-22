from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Department, Position, Employee, Attendance,
    Leave, Payroll, Document
)

User = get_user_model()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'manager', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(is_active=True)

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = [
            'title', 'department', 'description',
            'requirements', 'salary_range_min', 'salary_range_max'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name', 'middle_name', 'last_name',
            'national_id', 'birth_date', 'gender',
            'nationality', 'marital_status', 'photo',
            'email', 'mobile', 'phone',
            'address', 'emergency_contact',
            'employee_id', 'department', 'position',
            'hire_date', 'employment_type', 'salary',
            'bank_name', 'bank_account', 'iban',
            'id_copy', 'contract_copy', 'other_documents',
            'notes'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'emergency_contact': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.user_id:
            # إنشاء مستخدم جديد
            user = User.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            instance.user = user
        else:
            # تحديث بيانات المستخدم الحالي
            user = instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

        if commit:
            instance.save()
        return instance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'time_in', 'time_out', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = [
            'leave_type', 'start_date', 'end_date',
            'reason', 'attachment'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
        
        return cleaned_data

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee', 'month', 'year',
            'basic_salary', 'overtime', 'bonuses',
            'deductions', 'payment_method', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        employee = cleaned_data.get('employee')
        
        if month and year and employee:
            # التحقق من عدم وجود راتب سابق لنفس الشهر والسنة للموظف
            if Payroll.objects.filter(
                employee=employee,
                month=month,
                year=year
            ).exists():
                raise forms.ValidationError('يوجد راتب مسجل مسبقاً لهذا الموظف في نفس الشهر والسنة')
        
        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'employee', 'title', 'document_type',
            'file', 'description', 'expiry_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')
