# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-07 13:20


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20180315_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsor',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]