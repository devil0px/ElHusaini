# Generated by Django 5.1.5 on 2025-01-22 22:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("name", models.CharField(max_length=200, verbose_name="اسم العميل")),
                (
                    "client_type",
                    models.CharField(
                        choices=[
                            ("individual", "فرد"),
                            ("company", "شركة"),
                            ("government", "جهة حكومية"),
                        ],
                        max_length=20,
                        verbose_name="نوع العميل",
                    ),
                ),
                (
                    "contact_person",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="الشخص المسؤول"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="البريد الإلكتروني"
                    ),
                ),
                ("phone", models.CharField(max_length=20, verbose_name="رقم الهاتف")),
                (
                    "mobile",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="رقم الجوال"
                    ),
                ),
                ("address", models.TextField(verbose_name="العنوان")),
                (
                    "commercial_record",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="السجل التجاري"
                    ),
                ),
                (
                    "tax_number",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="الرقم الضريبي"
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
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_clients",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تم الإنشاء بواسطة",
                    ),
                ),
            ],
            options={
                "verbose_name": "عميل",
                "verbose_name_plural": "العملاء",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ClientContact",
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
                ("name", models.CharField(max_length=200, verbose_name="الاسم")),
                ("position", models.CharField(max_length=100, verbose_name="المنصب")),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="البريد الإلكتروني"
                    ),
                ),
                ("phone", models.CharField(max_length=20, verbose_name="رقم الهاتف")),
                (
                    "mobile",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="رقم الجوال"
                    ),
                ),
                (
                    "is_primary",
                    models.BooleanField(default=False, verbose_name="جهة اتصال رئيسية"),
                ),
                ("notes", models.TextField(blank=True, verbose_name="ملاحظات")),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contacts",
                        to="clients.client",
                        verbose_name="العميل",
                    ),
                ),
            ],
            options={
                "verbose_name": "جهة اتصال العميل",
                "verbose_name_plural": "جهات اتصال العميل",
                "ordering": ["-is_primary", "name"],
            },
        ),
        migrations.CreateModel(
            name="ClientDocument",
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
                    "document_type",
                    models.CharField(
                        choices=[
                            ("id", "هوية"),
                            ("commercial_record", "سجل تجاري"),
                            ("tax_certificate", "شهادة ضريبية"),
                            ("other", "أخرى"),
                        ],
                        max_length=20,
                        verbose_name="نوع المستند",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=200, verbose_name="عنوان المستند"),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="client_documents/", verbose_name="الملف"
                    ),
                ),
                (
                    "expiry_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="تاريخ الانتهاء"
                    ),
                ),
                (
                    "upload_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع"),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="clients.client",
                        verbose_name="العميل",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_client_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تم الرفع بواسطة",
                    ),
                ),
            ],
            options={
                "verbose_name": "مستند العميل",
                "verbose_name_plural": "مستندات العميل",
                "ordering": ["-upload_date"],
            },
        ),
        migrations.CreateModel(
            name="ClientMeeting",
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
                ("time", models.TimeField(verbose_name="الوقت")),
                ("location", models.CharField(max_length=200, verbose_name="المكان")),
                ("subject", models.CharField(max_length=200, verbose_name="الموضوع")),
                ("summary", models.TextField(verbose_name="ملخص الاجتماع")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "attendees",
                    models.ManyToManyField(
                        related_name="client_meetings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="الحاضرون",
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meetings",
                        to="clients.client",
                        verbose_name="العميل",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_meetings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="تم الإنشاء بواسطة",
                    ),
                ),
            ],
            options={
                "verbose_name": "اجتماع العميل",
                "verbose_name_plural": "اجتماعات العميل",
                "ordering": ["-date", "-time"],
            },
        ),
    ]
