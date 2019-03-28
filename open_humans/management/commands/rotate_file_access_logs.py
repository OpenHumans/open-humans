import datetime

from django.core.management.base import BaseCommand

from data_import.models import AWSDataFileAccessLog, NewDataFileAccessLog

LOG_ROTATE_DAYS = 120


class Command(BaseCommand):
    """
    A management command for rotating file access logs
    """

    help = "Expunge old log entries"

    def handle(self, *args, **options):
        self.stdout.write("Removing logs older than {0} days".format(LOG_ROTATE_DAYS))
        now = datetime.datetime.utcnow()
        # Note:  astimezone reapplies the timezone so that django doesn't
        # complain
        log_rotate_days_ago = (
            now - datetime.timedelta(days=LOG_ROTATE_DAYS)
        ).astimezone()
        aws_logs = AWSDataFileAccessLog.objects.filter(created__lte=log_rotate_days_ago)
        num_deletes = aws_logs.delete()[0]
        self.stdout.write("Removed {0} AWS log entries".format(num_deletes))
        oh_logs = NewDataFileAccessLog.objects.filter(date__lte=log_rotate_days_ago)
        num_deletes = oh_logs.delete()[0]
        self.stdout.write("Removed {0} Open Humans log entries".format(num_deletes))
