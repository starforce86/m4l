# Generated by Django 2.2.18 on 2021-02-23 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directories', '0022_affiliaterequest_request_as'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='affiliateship',
            unique_together={('directory', 'affiliate', 'connected_as')},
        ),
    ]