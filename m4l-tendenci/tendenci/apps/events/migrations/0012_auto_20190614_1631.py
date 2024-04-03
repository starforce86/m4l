# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-14 16:31


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_auto_20190221_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='gratuity',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='registrationconfiguration',
            name='gratuity_custom_option',
            field=models.BooleanField(default=False, verbose_name='Allow users to set their own gratuity'),
        ),
        migrations.AddField(
            model_name='registrationconfiguration',
            name='gratuity_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='registrationconfiguration',
            name='gratuity_options',
            field=models.CharField(blank=True, default='17%,18%,19%,20%', help_text='Comma separated numeric numbers in percentage. A "%" will be appended if the percent sign is not present.', max_length=100, verbose_name='Gratuity Options'),
        ),
    ]
