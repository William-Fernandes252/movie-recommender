# Generated by Django 4.2.10 on 2024-04-03 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exports", "0002_export_content_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="export",
            name="latest",
            field=models.BooleanField(default=True),
        ),
    ]