# Generated by Django 5.1.7 on 2025-03-23 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulador', '0005_auto_20250322_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='usuario',
            name='user_permissions',
        ),
        migrations.AlterField(
            model_name='usuario',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]
