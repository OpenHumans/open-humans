import arrow

from django.conf import settings
from django.core.management.base import BaseCommand

from private_sharing.models import ProjectDataFile


class Command(BaseCommand):
    """
    A management command for expunging incomplete project data files.

    A ProjectDataFile is incomplete when its `complete` attribute is set to
    False and more time has elapsed than the number of hours in
    INCOMPLETE_FILE_EXPIRATION_HOURS.
    """

    help = "Expunge incomplete project data files"

    def handle(self, *args, **options):
        self.stdout.write("Expunging incomplete project data files")

        expired_time = arrow.utcnow().replace(
            hours=-settings.INCOMPLETE_FILE_EXPIRATION_HOURS
        )

        # remove incomplete files older than the expiration time
        expunged_files = ProjectDataFile.all_objects.filter(
            created__lt=expired_time.datetime, completed=False
        ).delete()

        self.stdout.write("Removed {} data files".format(expunged_files))
