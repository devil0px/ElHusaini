from django.db import models
from django.conf import settings
from decimal import Decimal

class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('pending', 'قيد المراجعة'),
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('terminated', 'منتهي'),
        ('cancelled', 'ملغي'),
    ]
    
    CONTRACT_TYPE_CHOICES = [
        ('project', 'عقد مشروع'),
        ('service', 'عقد خدمة'),
        ('supply', 'عقد توريد'),
        ('maintenance', 'عقد صيانة'),
    ]
    
    contract_number = models.CharField('رقم العقد', max_length=50, unique=True)
    title = models.CharField('عنوان العقد', max_length=200)
    description = models.TextField('وصف العقد')
    contract_type = models.CharField('نوع العقد', max_length=20, choices=CONTRACT_TYPE_CHOICES)
    status = models.CharField('حالة العقد', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # العلاقات
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contracts', verbose_name='المشروع')
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='contracts', verbose_name='العميل')
    
    # التواريخ
    start_date = models.DateField('تاريخ البدء')
    end_date = models.DateField('تاريخ الانتهاء')
    signing_date = models.DateField('تاريخ التوقيع', null=True, blank=True)
    
    # المعلومات المالية
    total_value = models.DecimalField('القيمة الإجمالية', max_digits=14, decimal_places=2)
    advance_payment = models.DecimalField('الدفعة المقدمة', max_digits=14, decimal_places=2, default=0)
    retention_percentage = models.DecimalField('نسبة الاستقطاع', max_digits=5, decimal_places=2, default=0)
    
    # الملفات
    contract_file = models.FileField('ملف العقد', upload_to='contracts/', null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'عقد'
        verbose_name_plural = 'العقود'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_number} - {self.title}"

class ContractPayment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('advance', 'دفعة مقدمة'),
        ('progress', 'دفعة مرحلية'),
        ('final', 'دفعة نهائية'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'معتمد'),
        ('paid', 'مدفوع'),
        ('cancelled', 'ملغي'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments', verbose_name='العقد')
    payment_number = models.CharField('رقم الدفعة', max_length=50)
    payment_type = models.CharField('نوع الدفعة', max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField('المبلغ', max_digits=14, decimal_places=2)
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField('تاريخ الاستحقاق')
    payment_date = models.DateField('تاريخ الدفع', null=True, blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'دفعة عقد'
        verbose_name_plural = 'دفعات العقود'
        ordering = ['due_date']
        unique_together = ['contract', 'payment_number']
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.payment_number}"

class ContractClause(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='clauses', verbose_name='العقد')
    title = models.CharField('عنوان البند', max_length=200)
    content = models.TextField('محتوى البند')
    order = models.PositiveIntegerField('الترتيب', default=0)
    
    class Meta:
        verbose_name = 'بند العقد'
        verbose_name_plural = 'بنود العقد'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.title}"
