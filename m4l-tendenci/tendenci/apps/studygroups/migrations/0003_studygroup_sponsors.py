# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-03 16:50


from django.db import migrations
import tendenci.libs.tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0002_auto_20180315_0857'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='sponsors',
            field=tendenci.libs.tinymce.models.HTMLField(blank=True, default=''),
        ),
    ]