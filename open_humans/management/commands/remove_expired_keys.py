import datetime

from django.core.management.base import BaseCommand

from data_import.models import DataFileKey


class Command(BaseCommand):
    """
    A management command for expunging expired keys
    """

    help = 'Expunge expired keys'

    def handle(self, *args, **options):
        self.stdout.write('Expunging expired keys')
        now = datetime.datetime.utcnow()
        # Note:  astimezone reapplies the timezone so that django doesn't
        # complain
        six_hours_ago = (now - datetime.timedelta(hours=6)).astimezone()
        keys = DataFileKey.objects.filter(created__lte=six_hours_ago)
        num_deletes = keys.delete()[0]
        self.stdout.write('Removed {0} keys'.format(num_deletes))
