# Generated by Django 5.1.3 on 2024-11-26 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_remove_profile_age_quiz_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
