from datetime import datetime
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3

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
                log = []
                start_chars = ['"', "["]
                end_chars = ['"', "]"]
                tmp_index = 0
                for string in log_entry.split(" "):
                    if string[0] in start_chars:
                        if string[-1] not in end_chars:
                            tmp_index = len(log)
                    if (not tmp_index) or (tmp_index == len(log)):
                        log.append(string)
                        continue
                    log[tmp_index] = "{0} {1}".format(log[tmp_index], string)
                    if string[-1] in end_chars:
                        tmp_index = 0

                aws_log_entry = AWSDataFileAccessLog()
                aws_log_entry.bucket_owner = log[0]
                aws_log_entry.bucket = log[1]
                aws_log_entry.time = datetime.strptime(log[2], "[%d/%b/%Y:%H:%M:%S %z]")
                if log[3] != "-":
                    aws_log_entry.remote_ip = log[3]
                aws_log_entry.requester = log[4]
                aws_log_entry.request_id = log[5]
                aws_log_entry.operation = log[6]
                aws_log_entry.bucket_key = log[7]
                aws_log_entry.request_uri = log[8]
                aws_log_entry.status = int(log[9])
                aws_log_entry.error_code = log[10]
                if log[11] == "-":
                    log[11] = 0
                aws_log_entry.bytes_sent = int(log[11])
                if log[12] == "-":
                    log[12] = 0
                aws_log_entry.object_size = int(log[12])
                aws_log_entry.referrer = log[15]
                aws_log_entry.user_agent = log[16]
                aws_log_entry.host_id = log[17]
                aws_log_entry.signature_version = log[18]
                aws_log_entry.cipher_suite = log[19]
                aws_log_entry.auth_type = log[20]
                aws_log_entry.host_header = log[21]

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

            item.delete()
