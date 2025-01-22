from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

# Create your models here.

class Project(models.Model):
    class Meta:
        app_label = 'projects'
        
    STATUS_CHOICES = [
        ('planning', 'تخطيط'),
        ('in_progress', 'قيد التنفيذ'),
        ('on_hold', 'متوقف'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    name = models.CharField('اسم المشروع', max_length=200)
    code = models.CharField('رمز المشروع', max_length=50, unique=True)
    description = models.TextField('وصف المشروع')
    location = models.CharField('موقع المشروع', max_length=200)
    start_date = models.DateField('تاريخ البدء')
    end_date = models.DateField('تاريخ الانتهاء المتوقع')
    actual_end_date = models.DateField('تاريخ الانتهاء الفعلي', null=True, blank=True)
    status = models.CharField('حالة المشروع', max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # العلاقات
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='managed_projects',
        verbose_name='مدير المشروع'
    )
    
    # المعلومات المالية
    budget = models.DecimalField('الميزانية', max_digits=14, decimal_places=2, default=Decimal('0.00'))
    actual_cost = models.DecimalField('التكلفة الفعلية', max_digits=14, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'مشروع'
        verbose_name_plural = 'المشاريع'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

    def completed_phases_count(self):
        return self.phases.filter(completion_percentage=100).count()
    
    def total_phases_count(self):
        return self.phases.count()
    
    def completion_percentage(self):
        total = self.total_phases_count()
        if total > 0:
            return int((self.completed_phases_count() / total) * 100)
        return 0
    
    def is_delayed(self):
        return self.end_date < timezone.now().date() and self.status in ['planning', 'in_progress', 'on_hold']

class ProjectTeamMember(models.Model):
    class Meta:
        app_label = 'projects'
        verbose_name = 'عضو فريق المشروع'
        verbose_name_plural = 'أعضاء فريق المشروع'
        unique_together = ['project', 'user']
    
    ROLE_CHOICES = [
        ('project_manager', 'مدير المشروع'),
        ('team_member', 'عضو فريق'),
        ('consultant', 'مستشار'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_team_members', verbose_name='المشروع')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='المستخدم')
    member_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member', verbose_name='الدور')
    start_date = models.DateField(verbose_name='تاريخ البدء')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الانتهاء')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_member_role_display()}"

class ProjectPhase(models.Model):
    class Meta:
        app_label = 'projects'
        verbose_name = 'مرحلة المشروع'
        verbose_name_plural = 'مراحل المشروع'
        ordering = ['start_date']
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases', verbose_name='المشروع')
    name = models.CharField('اسم المرحلة', max_length=100)
    description = models.TextField('وصف المرحلة')
    start_date = models.DateField('تاريخ البدء')
    end_date = models.DateField('تاريخ الانتهاء المتوقع')
    actual_end_date = models.DateField('تاريخ الانتهاء الفعلي', null=True, blank=True)
    completion_percentage = models.DecimalField('نسبة الإنجاز', max_digits=5, decimal_places=2, default=0)
    budget = models.DecimalField('الميزانية', max_digits=14, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"

class ProjectDocument(models.Model):
    class Meta:
        app_label = 'projects'
        verbose_name = 'مستند المشروع'
        verbose_name_plural = 'مستندات المشروع'
        ordering = ['-upload_date']
    
    DOCUMENT_TYPES = [
        ('contract', 'عقد'),
        ('plan', 'مخطط'),
        ('permit', 'تصريح'),
        ('report', 'تقرير'),
        ('other', 'أخرى'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents', verbose_name='المشروع')
    title = models.CharField('عنوان المستند', max_length=200)
    document_type = models.CharField('نوع المستند', max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField('الملف', upload_to='project_documents/')
    description = models.TextField('وصف المستند', blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='تم الرفع بواسطة')
    upload_date = models.DateTimeField('تاريخ الرفع', auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.project.name}"
