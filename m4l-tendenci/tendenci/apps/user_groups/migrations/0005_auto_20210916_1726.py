# Generated by Django 2.2.24 on 2021-09-16 17:26

from django.db import migrations

def update_member_view(apps, schema_editor):
    Group = apps.get_model("user_groups", "Group")
    Group.objects.filter(allow_member_view=True).update(allow_member_view=False)

class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0004_auto_20200902_1545'),
    ]

    operations = [
        migrations.RunPython(update_member_view),
    ]
