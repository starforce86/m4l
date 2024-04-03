# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-15 17:19


from django.db import migrations


def remove_google_profile_from_page_view(apps, schema_editor):
    """
    Remove the google_profile block from pages/view.html
    
        {% if page.google_profile %}
          {% if page.has_google_author %}
          <a href="{{ page.google_profile }}?rel=author">{% trans "View Author's Google+ Profile" %}</a>
          {% elif page.has_google_publisher %}
          <a href="{{ page.google_profile }}" rel="publisher">{% trans "View Publisher's Google+ Page" %}</a>
          {% endif %}
        {% endif %}
    
    """
    import re
    import os
    from tendenci.apps.theme.utils import get_theme_root
    dir_path = get_theme_root()
    file_path = '{}/templates/pages/view.html'.format(dir_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            p = r'{0}([\d\D\s\S\w\W]*?){1}([\s\S]*?){2}'.format(re.escape('{% if page.google_profile %}'),
                                                                re.escape('{% endif %}'),
                                                                re.escape('{% endif %}'))
            content = re.sub(p, '', content)
            
        with open(file_path, 'w') as f:
            f.write(content)

class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_remove_page_google_profile'),
    ]

    operations = [
        migrations.RunPython(remove_google_profile_from_page_view)
    ]