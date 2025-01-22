from django.db import models
from django.conf import settings

# Create your models here.

class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('individual', 'فرد'),
        ('company', 'شركة'),
        ('government', 'جهة حكومية'),
    ]
    
    name = models.CharField('اسم العميل', max_length=200)
    client_type = models.CharField('نوع العميل', max_length=20, choices=CLIENT_TYPE_CHOICES)
    contact_person = models.CharField('الشخص المسؤول', max_length=200, blank=True)
    email = models.EmailField('البريد الإلكتروني', blank=True)
    phone = models.CharField('رقم الهاتف', max_length=20)
    mobile = models.CharField('رقم الجوال', max_length=20, blank=True)
    address = models.TextField('العنوان')
    
    # معلومات إضافية للشركات
    commercial_record = models.CharField('السجل التجاري', max_length=50, blank=True)
    tax_number = models.CharField('الرقم الضريبي', max_length=50, blank=True)
    
    notes = models.TextField('ملاحظات', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_clients',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ClientDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('id', 'هوية'),
        ('commercial_record', 'سجل تجاري'),
        ('tax_certificate', 'شهادة ضريبية'),
        ('other', 'أخرى'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents', verbose_name='العميل')
    document_type = models.CharField('نوع المستند', max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField('عنوان المستند', max_length=200)
    file = models.FileField('الملف', upload_to='client_documents/')
    expiry_date = models.DateField('تاريخ الانتهاء', null=True, blank=True)
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_client_documents',
        verbose_name='تم الرفع بواسطة'
    )
    upload_date = models.DateTimeField('تاريخ الرفع', auto_now_add=True)
    
    class Meta:
        verbose_name = 'مستند العميل'
        verbose_name_plural = 'مستندات العميل'
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.client.name} - {self.title}"

class ClientContact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts', verbose_name='العميل')
    name = models.CharField('الاسم', max_length=200)
    position = models.CharField('المنصب', max_length=100)
    email = models.EmailField('البريد الإلكتروني', blank=True)
    phone = models.CharField('رقم الهاتف', max_length=20)
    mobile = models.CharField('رقم الجوال', max_length=20, blank=True)
    is_primary = models.BooleanField('جهة اتصال رئيسية', default=False)
    notes = models.TextField('ملاحظات', blank=True)
    
    class Meta:
        verbose_name = 'جهة اتصال العميل'
        verbose_name_plural = 'جهات اتصال العميل'
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.client.name} - {self.name}"

class ClientMeeting(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='meetings', verbose_name='العميل')
    date = models.DateField('التاريخ')
    time = models.TimeField('الوقت')
    location = models.CharField('المكان', max_length=200)
    subject = models.CharField('الموضوع', max_length=200)
    summary = models.TextField('ملخص الاجتماع')
    
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='client_meetings',
        verbose_name='الحاضرون'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_meetings',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'اجتماع العميل'
        verbose_name_plural = 'اجتماعات العميل'
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.client.name} - {self.subject} ({self.date})"
