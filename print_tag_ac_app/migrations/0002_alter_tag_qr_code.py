# Generated by Django 5.0.7 on 2024-07-26 06:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("print_tag_ac_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="qr_code",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
