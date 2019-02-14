import arrow

from django.core.management.base import BaseCommand

from data_import.models import NewDataFileAccessLog


class Command(BaseCommand):
    """
    A management command for expunging IP addresses.
    """

    help = "Expunge IP addresses"

    def handle(self, *args, **options):
        self.stdout.write("Expunging addresses")

        ninety_days_ago = arrow.utcnow().replace(days=-90)

        # remove the IP address from all logs older than 90 days
        expunged_logs = NewDataFileAccessLog.objects.filter(
            date__lt=ninety_days_ago.datetime, ip_address__isnull=False
        ).update(ip_address=None)

        self.stdout.write("Removed {} IP addresses".format(expunged_logs))
