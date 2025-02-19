# Generated by Django 5.1.5 on 2025-01-22 22:18

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Expense",
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
                    "expense_type",
                    models.CharField(
                        choices=[
                            ("office", "مصاريف مكتبية"),
                            ("utilities", "مرافق"),
                            ("salaries", "رواتب"),
                            ("rent", "إيجار"),
                            ("maintenance", "صيانة"),
                            ("transport", "نقل"),
                            ("other", "أخرى"),
                        ],
                        max_length=20,
                        verbose_name="نوع المصروف",
                    ),
                ),
                ("description", models.CharField(max_length=255, verbose_name="الوصف")),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="المبلغ"
                    ),
                ),
                ("date", models.DateField(verbose_name="التاريخ")),
                (
                    "notes",
                    models.TextField(blank=True, null=True, verbose_name="ملاحظات"),
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
            ],
            options={
                "verbose_name": "مصروف",
                "verbose_name_plural": "المصروفات",
                "ordering": ["-date"],
            },
        ),
    ]
