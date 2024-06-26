# Generated by Django 3.2.18 on 2023-03-16 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tagging.fields
import tendenci.apps.base.fields
import tendenci.libs.tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chapters', '0013_auto_20220808_1704'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0006_auto_20200902_1545'),
        ('meta', '0001_initial'),
        ('user_groups', '0005_auto_20210916_1726'),
        ('entities', '0005_entity_show_for_donation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChapterPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=150)),
                ('owner_username', models.CharField(max_length=150)),
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('status_detail', models.CharField(default='active', max_length=50)),
                ('guid', models.CharField(max_length=40)),
                ('title', models.CharField(blank=True, max_length=500)),
                ('slug', tendenci.apps.base.fields.SlugField(db_index=True, max_length=100, verbose_name='URL Path')),
                ('content', tendenci.libs.tinymce.models.HTMLField()),
                ('view_contact_form', models.BooleanField(default=False)),
                ('design_notes', models.TextField(blank=True, verbose_name='Design Notes')),
                ('syndicate', models.BooleanField(default=False, verbose_name='Include in RSS feed')),
                ('template', models.CharField(blank=True, max_length=50, verbose_name='Template')),
                ('tags', tagging.fields.TagField(blank=True, max_length=255)),
                ('contributor_type', models.IntegerField(choices=[(1, 'Author'), (2, 'Publisher')], default=1)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='chapters.chapter')),
                ('creator', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chapter_pages_chapterpage_creator', to=settings.AUTH_USER_MODEL)),
                ('entity', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chapter_pages_chapterpage_entity', to='entities.entity')),
                ('group', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_groups.group')),
                ('header_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.headerimage')),
                ('meta', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.meta')),
                ('owner', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chapter_pages_chapterpage_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
