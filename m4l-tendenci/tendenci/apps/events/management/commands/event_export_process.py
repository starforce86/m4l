
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Directory export process.

    Usage:
        python manage.py event_export_process

        example:
        python manage.py event_export_process --start_dt=10/10/2010
                                              --end_dt=11/11/2011
                                              --type=1
                                              --identifier=1359048111
                                              --user=1
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--start_dt',
            action='store',
            dest='start_dt',
            default='',
            help='Export events whose start date is greater than or equal to the value specified')
        parser.add_argument(
            '--end_dt',
            action='store',
            dest='end_dt',
            default='',
            help='Export events whose start date is less than the value specified')
        parser.add_argument(
            '--type',
            action='store',
            dest='type',
            default='',
            help='Export events belonging to the type specified')
        parser.add_argument(
            '--identifier',
            action='store',
            dest='identifier',
            default='',
            help='Export file identifier')
        parser.add_argument(
            '--user',
            action='store',
            dest='user',
            default='1',
            help='Request user')

    def handle(self, *args, **options):
        from tendenci.apps.events.models import Type
        from tendenci.apps.events.utils import process_event_export

        start_dt = options['start_dt']
        end_dt = options['end_dt']
        type_id = options['type']
        user_id = options['user']
        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        if start_dt:
            try:
                start_dt = datetime.strptime(start_dt, '%m/%d/%Y')
            except:
                raise CommandError('Please use the following date format MM/DD/YYYY.\n')

        if end_dt:
            try:
                end_dt = datetime.strptime(end_dt, '%m/%d/%Y')
                end_dt = end_dt + timedelta(days=1)
            except:
                raise CommandError('Please use the following date format MM/DD/YYYY.\n')

        if type_id:
            try:
                type_id = Type.objects.get(pk=type_id)
            except:
                raise CommandError('Event type does not exist.')

        process_event_export(start_dt=start_dt,
                             end_dt=end_dt,
                             event_type=type_id,
                             identifier=identifier,
                             user_id=user_id)

        print('Event export done %s.' % identifier)
