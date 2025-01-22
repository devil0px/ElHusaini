from django.db import models
from django.conf import settings
from decimal import Decimal

class Category(models.Model):
    name = models.CharField('اسم الفئة', max_length=100)
    description = models.TextField('الوصف', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='الفئة الأم')
    
    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'الفئات'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField('اسم المورد', max_length=200)
    contact_person = models.CharField('الشخص المسؤول', max_length=200)
    email = models.EmailField('البريد الإلكتروني', blank=True)
    phone = models.CharField('رقم الهاتف', max_length=20)
    mobile = models.CharField('رقم الجوال', max_length=20, blank=True)
    address = models.TextField('العنوان')
    commercial_record = models.CharField('السجل التجاري', max_length=50, blank=True)
    tax_number = models.CharField('الرقم الضريبي', max_length=50, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_suppliers',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'مورد'
        verbose_name_plural = 'الموردين'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Item(models.Model):
    UNIT_CHOICES = [
        ('piece', 'قطعة'),
        ('meter', 'متر'),
        ('kg', 'كيلوجرام'),
        ('liter', 'لتر'),
        ('box', 'صندوق'),
        ('pack', 'حزمة'),
    ]
    
    code = models.CharField('الرمز', max_length=50, unique=True)
    name = models.CharField('اسم الصنف', max_length=200)
    description = models.TextField('الوصف', blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items', verbose_name='الفئة')
    unit = models.CharField('وحدة القياس', max_length=20, choices=UNIT_CHOICES)
    
    minimum_quantity = models.DecimalField('الحد الأدنى للكمية', max_digits=10, decimal_places=2, default=0)
    reorder_point = models.DecimalField('نقطة إعادة الطلب', max_digits=10, decimal_places=2, default=0)
    
    purchase_price = models.DecimalField('سعر الشراء', max_digits=10, decimal_places=2)
    selling_price = models.DecimalField('سعر البيع', max_digits=10, decimal_places=2)
    
    suppliers = models.ManyToManyField(Supplier, through='ItemSupplier', related_name='items', verbose_name='الموردين')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_items',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'صنف'
        verbose_name_plural = 'الأصناف'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class ItemSupplier(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='الصنف')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='المورد')
    price = models.DecimalField('السعر', max_digits=10, decimal_places=2)
    lead_time_days = models.PositiveIntegerField('مدة التوريد (أيام)', default=1)
    is_preferred = models.BooleanField('مورد مفضل', default=False)
    
    class Meta:
        verbose_name = 'مورد الصنف'
        verbose_name_plural = 'موردي الأصناف'
        unique_together = ['item', 'supplier']
    
    def __str__(self):
        return f"{self.item.name} - {self.supplier.name}"

class Stock(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('in', 'وارد'),
        ('out', 'صادر'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='stock_transactions', verbose_name='الصنف')
    transaction_type = models.CharField('نوع الحركة', max_length=3, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField('الكمية', max_digits=10, decimal_places=2)
    unit_price = models.DecimalField('سعر الوحدة', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('السعر الإجمالي', max_digits=14, decimal_places=2)
    
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions', verbose_name='المشروع')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions', verbose_name='المورد')
    
    reference_number = models.CharField('رقم المرجع', max_length=50, blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_transactions',
        verbose_name='تم الإنشاء بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'حركة مخزون'
        verbose_name_plural = 'حركات المخزون'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item.name} - {self.get_transaction_type_display()} - {self.quantity}"

class StockCount(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_counts', verbose_name='الصنف')
    count_date = models.DateField('تاريخ الجرد')
    physical_quantity = models.DecimalField('الكمية الفعلية', max_digits=10, decimal_places=2)
    system_quantity = models.DecimalField('كمية النظام', max_digits=10, decimal_places=2)
    difference = models.DecimalField('الفرق', max_digits=10, decimal_places=2)
    notes = models.TextField('ملاحظات', blank=True)
    
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_counts',
        verbose_name='تم الجرد بواسطة'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'جرد مخزون'
        verbose_name_plural = 'عمليات جرد المخزون'
        ordering = ['-count_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.count_date}"

class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('pending', 'قيد الموافقة'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
        ('ordered', 'تم الطلب'),
        ('received', 'تم الاستلام'),
        ('cancelled', 'ملغي'),
    ]
    
    request_number = models.CharField('رقم الطلب', max_length=50, unique=True)
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField('الأولوية', max_length=20, choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية')], default='medium')
    
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_requests', verbose_name='المشروع')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_requests', verbose_name='المورد')
    
    total_amount = models.DecimalField('المبلغ الإجمالي', max_digits=14, decimal_places=2, default=0)
    notes = models.TextField('ملاحظات', blank=True)
    
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requested_purchases', verbose_name='تم الطلب بواسطة')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchases', verbose_name='تم الاعتماد بواسطة')
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'طلب شراء'
        verbose_name_plural = 'طلبات الشراء'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_number} - {self.get_status_display()}"

class PurchaseRequestItem(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items', verbose_name='طلب الشراء')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='purchase_request_items', verbose_name='الصنف')
    quantity = models.DecimalField('الكمية', max_digits=10, decimal_places=2)
    unit_price = models.DecimalField('سعر الوحدة', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('السعر الإجمالي', max_digits=14, decimal_places=2)
    notes = models.TextField('ملاحظات', blank=True)
    
    class Meta:
        verbose_name = 'صنف طلب الشراء'
        verbose_name_plural = 'أصناف طلب الشراء'
    
    def __str__(self):
        return f"{self.purchase_request.request_number} - {self.item.name}"

class Warranty(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='warranties', verbose_name='الصنف')
    warranty_number = models.CharField('رقم الضمان', max_length=100)
    start_date = models.DateField('تاريخ البداية')
    end_date = models.DateField('تاريخ النهاية')
    provider = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='warranties', verbose_name='مزود الضمان')
    
    terms = models.TextField('شروط الضمان')
    coverage = models.TextField('تغطية الضمان')
    status = models.CharField('الحالة', max_length=20, choices=[('active', 'ساري'), ('expired', 'منتهي'), ('void', 'ملغي')], default='active')
    
    attachments = models.FileField('المرفقات', upload_to='warranty_attachments/', blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'ضمان'
        verbose_name_plural = 'الضمانات'
        ordering = ['-end_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.warranty_number}"

class Maintenance(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'صيانة وقائية'),
        ('corrective', 'صيانة تصحيحية'),
        ('emergency', 'صيانة طارئة'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'مجدول'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='maintenances', verbose_name='الصنف')
    maintenance_type = models.CharField('نوع الصيانة', max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    scheduled_date = models.DateTimeField('تاريخ الجدولة')
    start_date = models.DateTimeField('تاريخ البدء', null=True, blank=True)
    end_date = models.DateTimeField('تاريخ الانتهاء', null=True, blank=True)
    
    description = models.TextField('وصف الصيانة')
    cost = models.DecimalField('التكلفة', max_digits=10, decimal_places=2, default=0)
    provider = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances', verbose_name='مزود الخدمة')
    
    performed_by = models.CharField('تم التنفيذ بواسطة', max_length=200, blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_maintenances', verbose_name='تم الإنشاء بواسطة')
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'صيانة'
        verbose_name_plural = 'الصيانة'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.get_maintenance_type_display()} - {self.scheduled_date}"

class MaintenanceTask(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='tasks', verbose_name='الصيانة')
    description = models.CharField('الوصف', max_length=200)
    is_completed = models.BooleanField('مكتمل', default=False)
    notes = models.TextField('ملاحظات', blank=True)
    
    class Meta:
        verbose_name = 'مهمة صيانة'
        verbose_name_plural = 'مهام الصيانة'
    
    def __str__(self):
        return f"{self.maintenance.item.name} - {self.description}"

class SupplierEvaluation(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5 stars
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='evaluations', verbose_name='المورد')
    evaluation_date = models.DateField('تاريخ التقييم')
    
    quality_rating = models.IntegerField('تقييم الجودة', choices=RATING_CHOICES)
    delivery_rating = models.IntegerField('تقييم التسليم', choices=RATING_CHOICES)
    price_rating = models.IntegerField('تقييم السعر', choices=RATING_CHOICES)
    service_rating = models.IntegerField('تقييم الخدمة', choices=RATING_CHOICES)
    communication_rating = models.IntegerField('تقييم التواصل', choices=RATING_CHOICES)
    
    overall_rating = models.DecimalField('التقييم الإجمالي', max_digits=3, decimal_places=2)
    strengths = models.TextField('نقاط القوة', blank=True)
    weaknesses = models.TextField('نقاط الضعف', blank=True)
    recommendations = models.TextField('التوصيات', blank=True)
    
    evaluated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='supplier_evaluations', verbose_name='تم التقييم بواسطة')
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'تقييم مورد'
        verbose_name_plural = 'تقييمات الموردين'
        ordering = ['-evaluation_date']
        unique_together = ['supplier', 'evaluation_date']
    
    def __str__(self):
        return f"{self.supplier.name} - {self.evaluation_date}"
    
    def save(self, *args, **kwargs):
        # حساب التقييم الإجمالي
        ratings = [
            self.quality_rating,
            self.delivery_rating,
            self.price_rating,
            self.service_rating,
            self.communication_rating
        ]
        self.overall_rating = sum(ratings) / len(ratings)
        super().save(*args, **kwargs)

class InventoryAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('low_stock', 'مخزون منخفض'),
        ('expiry', 'قرب انتهاء الصلاحية'),
        ('maintenance_due', 'موعد صيانة'),
        ('warranty_expiry', 'انتهاء الضمان'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('resolved', 'تمت المعالجة'),
        ('ignored', 'تم التجاهل'),
    ]
    
    alert_type = models.CharField('نوع التنبيه', max_length=20, choices=ALERT_TYPE_CHOICES)
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='active')
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='alerts', verbose_name='الصنف')
    message = models.TextField('الرسالة')
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    resolved_at = models.DateTimeField('تاريخ المعالجة', null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        verbose_name='تمت المعالجة بواسطة'
    )
    
    class Meta:
        verbose_name = 'تنبيه مخزون'
        verbose_name_plural = 'تنبيهات المخزون'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.item.name}"
