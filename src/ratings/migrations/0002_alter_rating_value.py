# Generated by Django 4.2.11 on 2024-03-04 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ratings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rating",
            name="value",
            field=models.SmallIntegerField(
                blank=True,
                choices=[
                    (None, "Rate this"),
                    (1, "One"),
                    (2, "Two"),
                    (3, "Three"),
                    (4, "Four"),
                    (5, "Five"),
                ],
                null=True,
            ),
        ),
    ]