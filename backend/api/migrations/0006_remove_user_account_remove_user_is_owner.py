# Generated by Django 5.1.2 on 2024-12-23 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_account_subscription_plan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='account',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_owner',
        ),
    ]
