# Generated by Django 5.0.6 on 2024-06-18 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='user_answers',
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
    ]
