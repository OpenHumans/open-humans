import arrow

from django.conf import settings
from django.core.management.base import BaseCommand

from private_sharing.models import ProjectDataFile


class Command(BaseCommand):
    """
    A management command for expunging incomplete project data files.
    """

    help = 'Expunge incomplete project data files'

    def handle(self, *args, **options):
        self.stdout.write('Expunging incomplete project data files')

        expired_time = arrow.utcnow().replace(
            seconds=-settings.INCOMPLETE_DATA_FILE_EXPIRATION)

        # remove incomplete files older than the expiration time
        expunged_files = (ProjectDataFile.all_objects
                          .filter(created__lt=expired_time.datetime,
                                  completed=False)
                          .delete())

        self.stdout.write('Removed {} data files'.format(expunged_files))
