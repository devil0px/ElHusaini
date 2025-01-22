# Generated by Django 5.1.5 on 2025-01-22 22:18

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import hr.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="اسم القسم")),
                (
                    "code",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="كود القسم"
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="الوصف")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="managed_departments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="مدير القسم",
                    ),
                ),
            ],
            options={
                "verbose_name": "قسم",
                "verbose_name_plural": "أقسام",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        default="", max_length=50, verbose_name="الاسم الأول"
                    ),
                ),
                (
                    "middle_name",
                    models.CharField(
                        default="", max_length=50, verbose_name="اسم الأب"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        default="", max_length=50, verbose_name="اسم العائلة"
                    ),
                ),
                (
                    "national_id",
                    models.CharField(
                        default="0000000000",
                        max_length=10,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{10}$", "رقم الهوية يجب أن يتكون من 10 أرقام"
                            )
                        ],
                        verbose_name="رقم الهوية",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="تاريخ الميلاد"
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "ذكر"), ("F", "أنثى")],
                        default="M",
                        max_length=1,
                        verbose_name="الجنس",
                    ),
                ),
                (
                    "nationality",
                    models.CharField(default="", max_length=50, verbose_name="الجنسية"),
                ),
                (
                    "marital_status",
                    models.CharField(
                        choices=[
                            ("single", "أعزب"),
                            ("married", "متزوج"),
                            ("divorced", "مطلق"),
                            ("widowed", "أرمل"),
                        ],
                        default="single",
                        max_length=10,
                        verbose_name="الحالة الاجتماعية",
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=hr.models.employee_photo_path,
                        verbose_name="الصورة الشخصية",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        unique=True,
                        verbose_name="البريد الإلكتروني",
                    ),
                ),
                (
                    "mobile",
                    models.CharField(
                        default="0000000000",
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{10}$", "رقم الجوال يجب أن يتكون من 10 أرقام"
                            )
                        ],
                        verbose_name="رقم الجوال",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=10, null=True, verbose_name="رقم الهاتف"
                    ),
                ),
                ("address", models.TextField(default="", verbose_name="العنوان")),
                (
                    "emergency_contact",
                    models.TextField(
                        default="", verbose_name="جهة الاتصال في حالات الطوارئ"
                    ),
                ),
                (
                    "employee_id",
                    models.CharField(
                        default="0000000000",
                        max_length=10,
                        unique=True,
                        verbose_name="الرقم الوظيفي",
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        default="", max_length=100, verbose_name="المسمى الوظيفي"
                    ),
                ),
                (
                    "hire_date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="تاريخ التعيين"
                    ),
                ),
                (
                    "employment_type",
                    models.CharField(
                        choices=[
                            ("full_time", "دوام كامل"),
                            ("part_time", "دوام جزئي"),
                            ("contract", "عقد"),
                            ("temporary", "مؤقت"),
                        ],
                        default="full_time",
                        max_length=20,
                        verbose_name="نوع التوظيف",
                    ),
                ),
                (
                    "salary",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="الراتب",
                    ),
                ),
                (
                    "bank_name",
                    models.CharField(
                        default="", max_length=100, verbose_name="اسم البنك"
                    ),
                ),
                (
                    "bank_account",
                    models.CharField(
                        default="", max_length=20, verbose_name="رقم الحساب"
                    ),
                ),
                (
                    "iban",
                    models.CharField(
                        default="",
                        max_length=24,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^SA\\d{22}$",
                                "رقم الآيبان يجب أن يبدأ بـ SA متبوعاً بـ 22 رقم",
                            )
                        ],
                        verbose_name="رقم الآيبان",
                    ),
                ),
                (
                    "id_copy",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=hr.models.employee_document_path,
                        verbose_name="صورة الهوية",
                    ),
                ),
                (
                    "contract_copy",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=hr.models.employee_document_path,
                        verbose_name="نسخة العقد",
                    ),
                ),
                (
                    "other_documents",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=hr.models.employee_document_path,
                        verbose_name="وثائق أخرى",
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, null=True, verbose_name="ملاحظات"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="نشط")),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_employees",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تم الإنشاء بواسطة",
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="employees",
                        to="hr.department",
                        verbose_name="القسم",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="employee_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="المستخدم",
                    ),
                ),
            ],
            options={
                "verbose_name": "موظف",
                "verbose_name_plural": "الموظفين",
                "ordering": ["first_name", "middle_name", "last_name"],
            },
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="العنوان")),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("contract", "عقد عمل"),
                            ("id", "إثبات هوية"),
                            ("certificate", "شهادة"),
                            ("other", "أخرى"),
                        ],
                        max_length=20,
                        verbose_name="نوع المستند",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="hr/documents/%Y/%m/", verbose_name="الملف"
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="الوصف")),
                (
                    "expiry_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="تاريخ الانتهاء"
                    ),
                ),
                (
                    "is_verified",
                    models.BooleanField(default=False, verbose_name="تم التحقق"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="uploaded_hr_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تم الرفع بواسطة",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="hr.employee",
                        verbose_name="الموظف",
                    ),
                ),
            ],
            options={
                "verbose_name": "مستند",
                "verbose_name_plural": "مستندات",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Leave",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "leave_type",
                    models.CharField(
                        choices=[
                            ("annual", "سنوية"),
                            ("sick", "مرضية"),
                            ("unpaid", "بدون راتب"),
                            ("emergency", "طارئة"),
                            ("other", "أخرى"),
                        ],
                        max_length=20,
                        verbose_name="نوع الإجازة",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="تاريخ البداية")),
                ("end_date", models.DateField(verbose_name="تاريخ النهاية")),
                ("reason", models.TextField(verbose_name="السبب")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "قيد الانتظار"),
                            ("approved", "تمت الموافقة"),
                            ("rejected", "مرفوض"),
                            ("cancelled", "ملغي"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="الحالة",
                    ),
                ),
                (
                    "approved_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="تاريخ الموافقة"
                    ),
                ),
                (
                    "rejection_reason",
                    models.TextField(blank=True, verbose_name="سبب الرفض"),
                ),
                (
                    "attachment",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="hr/leaves/%Y/%m/",
                        verbose_name="مرفق",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_leaves",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تمت الموافقة بواسطة",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leaves",
                        to="hr.employee",
                        verbose_name="الموظف",
                    ),
                ),
            ],
            options={
                "verbose_name": "إجازة",
                "verbose_name_plural": "إجازات",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=100, verbose_name="المسمى الوظيفي"),
                ),
                ("description", models.TextField(verbose_name="الوصف الوظيفي")),
                (
                    "requirements",
                    models.TextField(blank=True, verbose_name="المتطلبات"),
                ),
                (
                    "salary_range_min",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="الحد الأدنى للراتب",
                    ),
                ),
                (
                    "salary_range_max",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="الحد الأقصى للراتب",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="positions",
                        to="hr.department",
                        verbose_name="القسم",
                    ),
                ),
            ],
            options={
                "verbose_name": "وظيفة",
                "verbose_name_plural": "وظائف",
                "ordering": ["department", "title"],
            },
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(verbose_name="التاريخ")),
                ("time_in", models.TimeField(verbose_name="وقت الحضور")),
                (
                    "time_out",
                    models.TimeField(
                        blank=True, null=True, verbose_name="وقت الانصراف"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("present", "حاضر"),
                            ("absent", "غائب"),
                            ("late", "متأخر"),
                            ("early_leave", "خروج مبكر"),
                            ("vacation", "إجازة"),
                            ("sick_leave", "إجازة مرضية"),
                        ],
                        max_length=20,
                        verbose_name="الحالة",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="ملاحظات")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance_records",
                        to="hr.employee",
                        verbose_name="الموظف",
                    ),
                ),
            ],
            options={
                "verbose_name": "حضور وانصراف",
                "verbose_name_plural": "حضور وانصراف",
                "ordering": ["-date", "-time_in"],
                "unique_together": {("employee", "date")},
            },
        ),
        migrations.CreateModel(
            name="Payroll",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "month",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(12),
                        ],
                        verbose_name="الشهر",
                    ),
                ),
                ("year", models.PositiveIntegerField(verbose_name="السنة")),
                (
                    "basic_salary",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="الراتب الأساسي"
                    ),
                ),
                (
                    "overtime",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="العمل الإضافي",
                    ),
                ),
                (
                    "bonuses",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="المكافآت",
                    ),
                ),
                (
                    "deductions",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="الخصومات",
                    ),
                ),
                (
                    "net_salary",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="صافي الراتب"
                    ),
                ),
                (
                    "is_paid",
                    models.BooleanField(default=False, verbose_name="تم الدفع"),
                ),
                (
                    "payment_date",
                    models.DateField(blank=True, null=True, verbose_name="تاريخ الدفع"),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("bank_transfer", "تحويل بنكي"),
                            ("cash", "نقدي"),
                            ("cheque", "شيك"),
                        ],
                        max_length=20,
                        verbose_name="طريقة الدفع",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="ملاحظات")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_payrolls",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تم الإنشاء بواسطة",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payrolls",
                        to="hr.employee",
                        verbose_name="الموظف",
                    ),
                ),
            ],
            options={
                "verbose_name": "راتب",
                "verbose_name_plural": "رواتب",
                "ordering": ["-year", "-month"],
                "permissions": [
                    ("can_view_payroll", "Can view payroll"),
                    ("can_generate_payroll", "Can generate payroll"),
                ],
                "unique_together": {("employee", "month", "year")},
            },
        ),
    ]
