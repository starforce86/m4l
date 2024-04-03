# Generated by Django 3.2.18 on 2023-03-22 09:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0005_entity_show_for_donation'),
        ('state_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateEditor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('state', models.ForeignKey(choices=[(4, 'Alabama'), (7, 'Alaska'), (8, 'Arizona'), (9, 'Arkansas'), (10, 'California'), (11, 'Colorado'), (12, 'Connecticut'), (13, 'Delaware'), (14, 'Florida'), (15, 'Georgia'), (16, 'Hawaii'), (17, 'Idaho'), (18, 'Illinois'), (19, 'Indiana'), (20, 'Iowa'), (21, 'Kansas'), (22, 'Kentucky'), (23, 'Louisiana'), (24, 'Maine'), (25, 'Maryland'), (26, 'Massachusetts'), (29, 'Michigan'), (30, 'Minnesota'), (31, 'Mississippi'), (32, 'Missouri'), (33, 'Montana'), (34, 'Nebraska'), (35, 'Nevada'), (36, 'New Hampshire'), (37, 'New Jersey'), (38, 'New Mexico'), (39, 'New York'), (40, 'North Carolina'), (41, 'North Dakota'), (42, 'Ohio'), (43, 'Oklahoma'), (44, 'Oregon'), (45, 'Pennsylvania'), (46, 'Rhode Island'), (47, 'South Carolina'), (48, 'South Dakota'), (49, 'Tennessee'), (50, 'Texas'), (51, 'Utah'), (52, 'Vermont'), (53, 'Virginia'), (54, 'Washington'), (55, 'West Virginia'), (56, 'Wisconsin'), (57, 'Wyoming')], on_delete=django.db.models.deletion.CASCADE, to='entities.entity')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'state')},
            },
        ),
    ]