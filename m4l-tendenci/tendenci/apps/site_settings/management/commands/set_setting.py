
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Example: python manage.py set_setting site global siteurl http://example.com
    """

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('scope')
        parser.add_argument('scope_category')
        parser.add_argument('name')
        parser.add_argument('value')

    def handle(self, scope=None, scope_category=None, name=None, value=None, **options):
        """
        Set the website theme via theme name
        """
        from tendenci.apps.site_settings.models import Setting
        from tendenci.apps.site_settings.utils import delete_all_settings_cache

        if scope and scope_category and name and value:
            try:
                setting = Setting.objects.get(
                    name=name,
                    scope=scope,
                    scope_category=scope_category,
                )
                setting.set_value(value)
                setting.save()
                
                setting.update_site_domain(value)

            except Setting.DoesNotExist:
                if int(options['verbosity']) > 0:
                    print("We could not update that setting.")
            delete_all_settings_cache()

            if name == "sitedisplayname":
                from tendenci.apps.user_groups.models import Group
                from tendenci.apps.entities.models import Entity
                try:
                    entity = Entity.objects.get(pk=1)
                    entity.entity_name = value
                    entity.save()
                except:
                    pass

                try:
                    group = Group.objects.get(pk=1)
                    group.name = value
                    group.label = value
                    group.slug = ''
                    group.save()
                except:
                    pass
