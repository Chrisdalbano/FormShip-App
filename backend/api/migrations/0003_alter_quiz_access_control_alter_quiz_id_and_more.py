# Generated by Django 5.1.2 on 2025-01-19 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_quiz_id_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='access_control',
            field=models.CharField(choices=[('public', 'Public'), ('invitation', 'Invitation'), ('login_required', 'Login')], default='public', help_text='Determines who can access the quiz.', max_length=20),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default='u92295841cf841789a24e4ba9a28250d', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
