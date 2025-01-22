from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

def employee_photo_path(instance, filename):
    return f'employees/{instance.employee_id}/photo/{filename}'

def employee_document_path(instance, filename):
    return f'employees/{instance.employee_id}/documents/{filename}'

class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', _('ذكر')),
        ('F', _('أنثى')),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('عقد')),
        ('temporary', _('مؤقت')),
    ]
    
    # ربط مع المستخدم
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name=_('المستخدم')
    )
    
    # البيانات الشخصية
    first_name = models.CharField(_('الاسم الأول'), max_length=50, default='')
    middle_name = models.CharField(_('اسم الأب'), max_length=50, default='')
    last_name = models.CharField(_('اسم العائلة'), max_length=50, default='')
    national_id = models.CharField(
        _('رقم الهوية'), 
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', _('رقم الهوية يجب أن يتكون من 10 أرقام'))],
        default='0000000000'
    )
    birth_date = models.DateField(_('تاريخ الميلاد'), default=timezone.now)
    gender = models.CharField(_('الجنس'), max_length=1, choices=GENDER_CHOICES, default='M')
    nationality = models.CharField(_('الجنسية'), max_length=50, default='')
    marital_status = models.CharField(_('الحالة الاجتماعية'), max_length=10, choices=MARITAL_STATUS_CHOICES, default='single')
    photo = models.ImageField(_('الصورة الشخصية'), upload_to=employee_photo_path, null=True, blank=True)
    
    # معلومات الاتصال
    email = models.EmailField(_('البريد الإلكتروني'), unique=True, null=True, blank=True)
    mobile = models.CharField(
        _('رقم الجوال'),
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', _('رقم الجوال يجب أن يتكون من 10 أرقام'))],
        default='0000000000'
    )
    phone = models.CharField(_('رقم الهاتف'), max_length=10, null=True, blank=True)
    address = models.TextField(_('العنوان'), default='')
    emergency_contact = models.TextField(_('جهة الاتصال في حالات الطوارئ'), default='')
    
    # معلومات الوظيفة
    employee_id = models.CharField(_('الرقم الوظيفي'), max_length=10, unique=True, default='0000000000')
    department = models.ForeignKey(
        'Department',
        verbose_name=_('القسم'),
        on_delete=models.PROTECT,
        related_name='employees',
        null=True
    )
    position = models.CharField(_('المسمى الوظيفي'), max_length=100, default='')
    hire_date = models.DateField(_('تاريخ التعيين'), default=timezone.now)
    employment_type = models.CharField(_('نوع التوظيف'), max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    salary = models.DecimalField(_('الراتب'), max_digits=10, decimal_places=2, default=0)
    
    # معلومات البنك
    bank_name = models.CharField(_('اسم البنك'), max_length=100, default='')
    bank_account = models.CharField(_('رقم الحساب'), max_length=20, default='')
    iban = models.CharField(
        _('رقم الآيبان'),
        max_length=24,
        validators=[RegexValidator(r'^SA\d{22}$', _('رقم الآيبان يجب أن يبدأ بـ SA متبوعاً بـ 22 رقم'))],
        default=''
    )
    
    # الوثائق
    id_copy = models.FileField(_('صورة الهوية'), upload_to=employee_document_path, null=True, blank=True)
    contract_copy = models.FileField(_('نسخة العقد'), upload_to=employee_document_path, null=True, blank=True)
    other_documents = models.FileField(_('وثائق أخرى'), upload_to=employee_document_path, null=True, blank=True)
    
    # معلومات إضافية
    notes = models.TextField(_('ملاحظات'), null=True, blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('تم الإنشاء بواسطة'),
        on_delete=models.PROTECT,
        related_name='created_employees',
        null=True
    )
    
    class Meta:
        verbose_name = _('موظف')
        verbose_name_plural = _('الموظفين')
        ordering = ['first_name', 'middle_name', 'last_name']
    
    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
    
    def get_full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
    
    def get_short_name(self):
        return f'{self.first_name} {self.last_name}'

class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name='الموظف'
    )
    date = models.DateField('التاريخ')
    time_in = models.TimeField('وقت الحضور')
    time_out = models.TimeField('وقت الانصراف', null=True, blank=True)
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=[
            ('present', 'حاضر'),
            ('absent', 'غائب'),
            ('late', 'متأخر'),
            ('early_leave', 'خروج مبكر'),
            ('vacation', 'إجازة'),
            ('sick_leave', 'إجازة مرضية'),
        ]
    )
    notes = models.TextField('ملاحظات', blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.date}"

    def duration(self):
        if self.time_out:
            return self.time_out - self.time_in
        return None

    class Meta:
        verbose_name = 'حضور وانصراف'
        verbose_name_plural = 'حضور وانصراف'
        ordering = ['-date', '-time_in']
        unique_together = ['employee', 'date']

class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('annual', 'سنوية'),
        ('sick', 'مرضية'),
        ('unpaid', 'بدون راتب'),
        ('emergency', 'طارئة'),
        ('other', 'أخرى'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
        ('cancelled', 'ملغي'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leaves',
        verbose_name='الموظف'
    )
    leave_type = models.CharField('نوع الإجازة', max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField('تاريخ البداية')
    end_date = models.DateField('تاريخ النهاية')
    reason = models.TextField('السبب')
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name='تمت الموافقة بواسطة'
    )
    approved_at = models.DateTimeField('تاريخ الموافقة', null=True, blank=True)
    rejection_reason = models.TextField('سبب الرفض', blank=True)
    attachment = models.FileField(
        'مرفق',
        upload_to='hr/leaves/%Y/%m/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"

    def duration(self):
        return (self.end_date - self.start_date).days + 1

    class Meta:
        verbose_name = 'إجازة'
        verbose_name_plural = 'إجازات'
        ordering = ['-created_at']

class Payroll(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='payrolls',
        verbose_name='الموظف'
    )
    month = models.PositiveIntegerField(
        'الشهر',
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveIntegerField('السنة')
    basic_salary = models.DecimalField('الراتب الأساسي', max_digits=10, decimal_places=2)
    overtime = models.DecimalField('العمل الإضافي', max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField('المكافآت', max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField('الخصومات', max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField('صافي الراتب', max_digits=10, decimal_places=2)
    is_paid = models.BooleanField('تم الدفع', default=False)
    payment_date = models.DateField('تاريخ الدفع', null=True, blank=True)
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=[
            ('bank_transfer', 'تحويل بنكي'),
            ('cash', 'نقدي'),
            ('cheque', 'شيك'),
        ]
    )
    notes = models.TextField('ملاحظات', blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_payrolls',
        verbose_name='تم الإنشاء بواسطة'
    )

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"

    def save(self, *args, **kwargs):
        self.net_salary = (
            self.basic_salary +
            self.overtime +
            self.bonuses -
            self.deductions
        )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'راتب'
        verbose_name_plural = 'رواتب'
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']
        permissions = [
            ('can_view_payroll', 'Can view payroll'),
            ('can_generate_payroll', 'Can generate payroll'),
        ]

class Department(models.Model):
    name = models.CharField('اسم القسم', max_length=100)
    code = models.CharField('كود القسم', max_length=20, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_departments',
        verbose_name='مدير القسم'
    )
    description = models.TextField('الوصف', blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'أقسام'
        ordering = ['name']

class Position(models.Model):
    title = models.CharField('المسمى الوظيفي', max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='positions',
        verbose_name='القسم'
    )
    description = models.TextField('الوصف الوظيفي')
    requirements = models.TextField('المتطلبات', blank=True)
    salary_range_min = models.DecimalField(
        'الحد الأدنى للراتب',
        max_digits=10,
        decimal_places=2
    )
    salary_range_max = models.DecimalField(
        'الحد الأقصى للراتب',
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.department}"

    class Meta:
        verbose_name = 'وظيفة'
        verbose_name_plural = 'وظائف'
        ordering = ['department', 'title']

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'عقد عمل'),
        ('id', 'إثبات هوية'),
        ('certificate', 'شهادة'),
        ('other', 'أخرى'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='الموظف'
    )
    title = models.CharField('العنوان', max_length=200)
    document_type = models.CharField('نوع المستند', max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField('الملف', upload_to='hr/documents/%Y/%m/')
    description = models.TextField('الوصف', blank=True)
    expiry_date = models.DateField('تاريخ الانتهاء', null=True, blank=True)
    is_verified = models.BooleanField('تم التحقق', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='uploaded_hr_documents',
        verbose_name='تم الرفع بواسطة'
    )

    def __str__(self):
        return f"{self.title} - {self.employee}"

    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    class Meta:
        verbose_name = 'مستند'
        verbose_name_plural = 'مستندات'
        ordering = ['-created_at']
