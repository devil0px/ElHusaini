from django.db import models
from django.conf import settings

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('project_progress', 'تقرير تقدم المشروع'),
        ('financial', 'تقرير مالي'),
        ('hr', 'تقرير موارد بشرية'),
        ('inventory', 'تقرير مخزون'),
        ('client', 'تقرير عملاء'),
        ('contract', 'تقرير عقود'),
        ('custom', 'تقرير مخصص'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('pending', 'قيد المراجعة'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
    ]
    
    title = models.CharField('عنوان التقرير', max_length=200)
    report_type = models.CharField('نوع التقرير', max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField('وصف التقرير')
    content = models.TextField('محتوى التقرير')
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # العلاقات
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='reports', verbose_name='المشروع')
    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, null=True, blank=True, related_name='reports', verbose_name='العقد')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, null=True, blank=True, related_name='reports', verbose_name='الموظف')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports',
        verbose_name='تم الإنشاء بواسطة'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports',
        verbose_name='تم الاعتماد بواسطة'
    )
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'تقرير'
        verbose_name_plural = 'التقارير'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

class ReportAttachment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='attachments', verbose_name='التقرير')
    title = models.CharField('عنوان المرفق', max_length=200)
    file = models.FileField('الملف', upload_to='report_attachments/')
    description = models.TextField('وصف المرفق', blank=True)
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='report_attachments',
        verbose_name='تم الرفع بواسطة'
    )
    upload_date = models.DateTimeField('تاريخ الرفع', auto_now_add=True)
    
    class Meta:
        verbose_name = 'مرفق التقرير'
        verbose_name_plural = 'مرفقات التقرير'
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.report.title} - {self.title}"

class ReportTemplate(models.Model):
    name = models.CharField('اسم القالب', max_length=200)
    report_type = models.CharField('نوع التقرير', max_length=20, choices=Report.REPORT_TYPE_CHOICES)
    description = models.TextField('وصف القالب')
    template_content = models.TextField('محتوى القالب')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'قالب تقرير'
        verbose_name_plural = 'قوالب التقارير'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class ReportSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules', verbose_name='قالب التقرير')
    frequency = models.CharField('التكرار', max_length=20, choices=FREQUENCY_CHOICES)
    next_run = models.DateTimeField('التشغيل القادم')
    is_active = models.BooleanField('نشط', default=True)
    
    # العلاقات الاختيارية
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='report_schedules', verbose_name='المشروع')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, null=True, blank=True, related_name='report_schedules', verbose_name='الموظف')
    
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='report_subscriptions',
        verbose_name='المستلمون'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'جدولة تقرير'
        verbose_name_plural = 'جدولة التقارير'
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_frequency_display()}"
