# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-16 18:20


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0003_auto_20181008_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='void_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='void_reason',
            field=models.TextField(blank=True, default='', max_length=200, verbose_name='Reason to void'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='voided_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_voided_by', to=settings.AUTH_USER_MODEL),
        ),
    ]