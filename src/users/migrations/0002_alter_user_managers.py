# Generated by Django 4.2.10 on 2024-04-01 14:08

from django.db import migrations
import users.managers


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", users.managers.UserManager()),
            ],
        ),
    ]
