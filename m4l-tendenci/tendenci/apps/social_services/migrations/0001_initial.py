# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
import django.contrib.gis.db.models.fields
import tendenci.libs.tinymce.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReliefAssessment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_number', models.CharField(max_length=50, null=True, verbose_name='ID number', blank=True)),
                ('issuing_authority', models.CharField(max_length=100, null=True, verbose_name='issuing authority', blank=True)),
                ('health_insurance', models.BooleanField(default=False, verbose_name='health insurance')),
                ('insurance_provider', models.CharField(max_length=100, null=True, verbose_name='insurance provider', blank=True)),
                ('address', models.CharField(max_length=150, verbose_name='address')),
                ('address2', models.CharField(max_length=100, null=True, verbose_name='address2', blank=True)),
                ('city', models.CharField(max_length=50, verbose_name='city')),
                ('state', models.CharField(max_length=50, verbose_name='state')),
                ('zipcode', models.CharField(max_length=50, verbose_name='ZIP')),
                ('country', models.CharField(max_length=50, verbose_name='country')),
                ('alt_address', models.CharField(max_length=150, null=True, verbose_name='address', blank=True)),
                ('alt_address2', models.CharField(max_length=100, null=True, verbose_name='address2', blank=True)),
                ('alt_city', models.CharField(max_length=50, null=True, verbose_name='city', blank=True)),
                ('alt_state', models.CharField(max_length=50, null=True, verbose_name='state', blank=True)),
                ('alt_zipcode', models.CharField(max_length=50, null=True, verbose_name='ZIP', blank=True)),
                ('alt_country', models.CharField(max_length=50, null=True, verbose_name='country', blank=True)),
                ('ethnicity', models.CharField(blank=True, max_length=10, null=True, verbose_name='', choices=[('black', 'Black'), ('caucasian', 'Caucasian'), ('hispanic', 'Hispanic'), ('asian', 'Asian'), ('other', 'Other')])),
                ('other_ethnicity', models.CharField(help_text='Specify here if your ethnicity is not included above.', max_length=50, null=True, verbose_name='', blank=True)),
                ('below_2', models.IntegerField(null=True, verbose_name='0 - 2 yrs', blank=True)),
                ('between_3_11', models.IntegerField(null=True, verbose_name='3 - 11 yrs', blank=True)),
                ('between_12_18', models.IntegerField(null=True, verbose_name='12 - 18 yrs', blank=True)),
                ('between_19_59', models.IntegerField(null=True, verbose_name='19 - 59 yrs', blank=True)),
                ('above_60', models.IntegerField(null=True, verbose_name='over 60 yrs', blank=True)),
                ('ssa', models.BooleanField(default=False, help_text='current recipient of Social Security', verbose_name='social security administration')),
                ('dhs', models.BooleanField(default=False, help_text='food stamps, WIC, TANF', verbose_name='department human services')),
                ('children_needs', models.BooleanField(default=False, help_text='school supplies, uniforms, clothing, child care, diapers, wipes', verbose_name='children needs')),
                ('toiletries', models.BooleanField(default=False, verbose_name='toiletries')),
                ('employment', models.BooleanField(default=False, verbose_name='employment')),
                ('training', models.BooleanField(default=False, verbose_name='training')),
                ('food', models.BooleanField(default=False, verbose_name='food')),
                ('gas', models.BooleanField(default=False, verbose_name='gas')),
                ('prescription', models.BooleanField(default=False, verbose_name='prescription care')),
                ('other_service', models.CharField(help_text='Specify additional services needed.', max_length=100, null=True, verbose_name='other', blank=True)),
                ('case_notes', tendenci.libs.tinymce.models.HTMLField(null=True, verbose_name='case notes', blank=True)),
                ('items_provided', tendenci.libs.tinymce.models.HTMLField(null=True, verbose_name='items provided', blank=True)),
                ('loc', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SkillSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paramedic', models.BooleanField(default=False, verbose_name='paramedic')),
                ('fireman', models.BooleanField(default=False, verbose_name='fireman trained')),
                ('first_aid', models.BooleanField(default=False, verbose_name='first aid')),
                ('safety_manager', models.BooleanField(default=False, verbose_name='safety manager')),
                ('police', models.BooleanField(default=False, verbose_name='police')),
                ('search_and_rescue', models.BooleanField(default=False, verbose_name='search and rescue')),
                ('scuba_certified', models.BooleanField(default=False, verbose_name='scuba certified')),
                ('crowd_control', models.BooleanField(default=False, verbose_name='crowd control')),
                ('truck', models.BooleanField(default=False, verbose_name='truck driver')),
                ('pilot', models.BooleanField(default=False, verbose_name='pilot')),
                ('aircraft', models.CharField(max_length=100, null=True, verbose_name='aircraft', blank=True)),
                ('ship', models.BooleanField(default=False, verbose_name='ship captain')),
                ('sailor', models.BooleanField(default=False, verbose_name='sailor')),
                ('doctor', models.BooleanField(default=False, verbose_name='medical doctor')),
                ('nurse', models.BooleanField(default=False, verbose_name='nurse')),
                ('medical_specialty', models.CharField(max_length=100, null=True, verbose_name='medical specialty', blank=True)),
                ('crisis_communication', models.BooleanField(default=False, verbose_name='crisis communications')),
                ('media', models.BooleanField(default=False, verbose_name='media')),
                ('author', models.BooleanField(default=False, verbose_name='author')),
                ('public_speaker', models.BooleanField(default=False, verbose_name='public speaker')),
                ('politician', models.BooleanField(default=False, verbose_name='politician')),
                ('blogger', models.BooleanField(default=False, verbose_name='blogger')),
                ('photographer', models.BooleanField(default=False, verbose_name='photographer')),
                ('videographer', models.BooleanField(default=False, verbose_name='videographer')),
                ('radio_operator', models.BooleanField(default=False, verbose_name='radio operator')),
                ('call_sign', models.CharField(max_length=100, null=True, verbose_name='call sign', blank=True)),
                ('actor', models.BooleanField(default=False, verbose_name='actor')),
                ('thought_leader', models.BooleanField(default=False, verbose_name='thought leader')),
                ('influencer', models.BooleanField(default=False, verbose_name='influencer')),
                ('languages', models.CharField(max_length=200, null=True, verbose_name='languages spoken', blank=True)),
                ('teacher', models.BooleanField(default=False, verbose_name='teacher')),
                ('school_admin', models.BooleanField(default=False, verbose_name='school administrator')),
                ('military_rank', models.CharField(max_length=100, null=True, verbose_name='military rank', blank=True)),
                ('military_training', models.BooleanField(default=False, verbose_name='military training')),
                ('desert_trained', models.BooleanField(default=False, verbose_name='desert trained')),
                ('cold_trained', models.BooleanField(default=False, verbose_name='cold weather trained')),
                ('marksman', models.BooleanField(default=False, verbose_name='marksman')),
                ('security_clearance', models.CharField(max_length=200, null=True, verbose_name='security clearance', blank=True)),
                ('loc', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
