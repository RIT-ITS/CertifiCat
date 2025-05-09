# Generated by Django 5.1.2 on 2025-03-14 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acme", "0007_rename_tempusagehack_usage"),
    ]

    operations = [
        migrations.CreateModel(
            name="TermsOfService",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("text", models.TextField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterModelOptions(
            name="accountbindinggroupscope",
            options={"ordering": ("group__name",)},
        ),
    ]
