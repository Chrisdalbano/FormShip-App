# Generated by Django 5.1.2 on 2025-01-28 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_sharedquiz_id_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharedquiz',
            name='id',
            field=models.CharField(default='shb3dcbdee202501280552', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default='uad617050202501280552', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
