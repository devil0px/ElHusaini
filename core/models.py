from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """
    An abstract base class model that provides common fields
    for most models in the system.
    """
    is_active = models.BooleanField(_('نشط'), default=True)
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        abstract = True


class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('office', 'مصاريف مكتبية'),
        ('utilities', 'مرافق'),
        ('salaries', 'رواتب'),
        ('rent', 'إيجار'),
        ('maintenance', 'صيانة'),
        ('transport', 'نقل'),
        ('other', 'أخرى')
    ]
    
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES, verbose_name='نوع المصروف')
    description = models.CharField(max_length=255, verbose_name='الوصف')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المبلغ')
    date = models.DateField(verbose_name='التاريخ')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'مصروف'
        verbose_name_plural = 'المصروفات'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.amount}"
