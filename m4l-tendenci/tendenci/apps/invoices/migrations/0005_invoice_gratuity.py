# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-14 16:35


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0004_auto_20181016_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='gratuity',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=6),
        ),
    ]
