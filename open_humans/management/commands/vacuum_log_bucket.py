from datetime import datetime
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3
from pyparsing import ZeroOrMore, Regex

from data_import.models import DataFile, AWSDataFileAccessLog, NewDataFileAccessLog
from data_import.serializers import serialize_datafile_to_dict


AWS_LOG_KEY_BLACKLIST = ["favicon.ico"]


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

                # This here solution brought to you by Stack Overflow:
                # https://stackoverflow.com/questions/27303977/split-string-at-double-quotes-and-box-brackets
                parser = ZeroOrMore(
                    Regex(r"\[[^]]*\]") | Regex(r'"[^"]*"') | Regex(r"[^ ]+")
                )
                log = list(parser.parseString(log_entry))

                if log[4] == "AmazonS3":
                    # Internal S3 operation, can be skipped
                    continue

                aws_log_entry = AWSDataFileAccessLog()
                fields = [
                    "bucket_owner",
                    "bucket",
                    "time",
                    "remote_ip",
                    "requester",
                    "request_id",
                    "operation",
                    "bucket_key",
                    "request_uri",
                    "status",
                    "error_code",
                    "bytes_sent",
                    "object_size",
                    "total_time",
                    "turn_around_time",
                    "referrer",
                    "user_agent",
                    "version_id",
                    "host_id",
                    "signature_version",
                    "cipher_suite",
                    "auth_type",
                    "host_header",
                ]
                for index, field_name in enumerate(fields):
                    field = aws_log_entry._meta.get_field(field_name)
                    if field.get_internal_type() == "IntegerField":
                        log_item = log[index]
                        if (log_item == "-") or (log_item == '"-"'):
                            log_item = 0
                        log[index] = int(log_item)
                    if field.get_internal_type() == "DateTimeField":
                        log[index] = datetime.strptime(
                            log[index], "[%d/%b/%Y:%H:%M:%S %z]"
                        )
                    if index == 17:
                        # Sometimes, aws inserts a stray '-' here, klugey workaround
                        if (log[17] == "-") and (len(log[18]) < 32):
                            # The actual Host ID is always quite long
                            log.pop(17)

                    setattr(aws_log_entry, field_name, log[index])

                url = aws_log_entry.request_uri.split(" ")[1]
                # Split out the key from the url
                parsed_url = urlparse(url)
                # parse_qs returns a dict with lists as values
                oh_key = parse_qs(parsed_url.query).get("x-oh-key", [""])[0]

                if oh_key == "None":
                    oh_key = None
                if oh_key:
                    oh_data_file_access_logs = NewDataFileAccessLog.objects.filter(
                        data_file_key__key=oh_key
                    )
                else:
                    oh_data_file_access_logs = None
                data_file = DataFile.objects.filter(file=aws_log_entry.bucket_key)
                if data_file:
                    if data_file.count() == 1:
                        aws_log_entry.serialized_data_file = serialize_datafile_to_dict(
                            data_file.get()
                        )

                    elif oh_data_file_access_logs:
                        aws_log_entry.serialized_data_file = serialize_datafile_to_dict(
                            oh_data_file_access_logs.get().data_file
                        )
                    else:
                        aws_log_entry.serialized_data_file = None

                # Filter out things we don't care to log
                if settings.AWS_STORAGE_BUCKET_NAME in url:
                    continue
                if any(
                    blacklist_item in url for blacklist_item in AWS_LOG_KEY_BLACKLIST
                ):
                    continue
                aws_log_entry.save()

                # Associate with any potential access logs from the Open Humans end.
                if oh_data_file_access_logs:
                    aws_log_entry.oh_data_file_access_log.set(oh_data_file_access_logs)

            item.delete()
