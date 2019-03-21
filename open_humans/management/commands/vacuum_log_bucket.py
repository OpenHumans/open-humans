from datetime import datetime
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3
from pyparsing import ZeroOrMore, Regex

from data_import.models import DataFile, AWSDataFileAccessLog, NewDataFileAccessLog


class Command(BaseCommand):
    """
    A management command vaccuming up file access logs and putting them in the database.
    """

    help = "Populates database with file access logs"

    def handle(self, *args, **options):
        self.stdout.write("Retreiving file access logs")
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(settings.LOG_BUCKET)
        for item in bucket.objects.all():
            log_objects = item.get()["Body"].read().decode("utf-8").split("\n")
            for log_entry in log_objects:
                if not log_entry:
                    continue
                parser = ZeroOrMore(
                    Regex(r"\[[^]]*\]") | Regex(r'"[^"]*"') | Regex(r"[^ ]+")
                )
                log = list(parser.parseString(log_entry))

                aws_log_entry = AWSDataFileAccessLog()
                skip_fields = ["id", "created", "data_file", "oh_data_file_access_log"]
                fields = [
                    field
                    for field in aws_log_entry._meta.get_fields()
                    if field.name not in skip_fields
                ]
                for index, field in enumerate(fields):
                    if field.get_internal_type() == "IntegerField":
                        log_item = log[index]
                        if (log_item == "-") or (log_item == '"-"'):
                            log_item = 0
                        log[index] = int(log_item)
                    if field.get_internal_type() == "DateTimeField":
                        log[index] = datetime.strptime(
                            log[index], "[%d/%b/%Y:%H:%M:%S %z]"
                        )
                    setattr(aws_log_entry, field.name, log[index])

                data_file = DataFile.objects.filter(file=aws_log_entry.bucket_key)
                if data_file:
                    aws_log_entry.data_file = data_file.get()
                url = aws_log_entry.request_uri.split(" ")[1]

                # Filter out things we don't care to log
                if settings.AWS_STORAGE_BUCKET_NAME in url:
                    continue
                if any(
                    blacklist_item in url
                    for blacklist_item in settings.AWS_LOG_KEY_BLACKLIST
                ):
                    continue
                aws_log_entry.save()

                # Associate with any potential access logs from the Open Humans end.

                # Split out the key from the url
                parsed_url = urlparse(url)
                # parse_qs returns a dict with lists as values
                oh_key = parse_qs(parsed_url.query).get("x-oh-key", [""])[0]
                if oh_key == "None":
                    oh_key = None
                if oh_key:
                    oh_data_file_access_logs = NewDataFileAccessLog.objects.filter(
                        key=oh_key
                    )
                    aws_log_entry.oh_data_file_access_log.set(oh_data_file_access_logs)

            # item.delete()
