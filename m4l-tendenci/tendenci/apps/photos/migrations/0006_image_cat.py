# Generated by Django 3.2.12 on 2022-06-21 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0005_auto_20220607_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='cat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cat_photos', to='photos.photocategory', verbose_name='Category'),
        ),
    ]
