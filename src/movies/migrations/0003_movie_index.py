# Generated by Django 4.2.10 on 2024-04-02 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0002_movie_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="movie",
            name="index",
            field=models.BigIntegerField(
                blank=True, help_text="Position index for embeddings", null=True
            ),
        ),
    ]
