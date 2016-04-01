#!/usr/bin/env python
# pylint: disable=wrong-import-order

import boto3
import os
import re

from env_tools import apply_env

apply_env()

import django  # noqa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

django.setup()

from data_import.models import DataFile  # noqa
from data_import.utils import get_upload_path  # noqa

BUCKET_NAME = 'open-humans-production'

s3 = boto3.resource('s3')

bucket = s3.Bucket(BUCKET_NAME)

for key in bucket.objects.all():
    if not re.match(r'^member/', key.key):
        continue

    if 'profile-images' in key.key:
        continue

    try:
        data_file = DataFile.objects.get(file=key.key)
    except DataFile.DoesNotExist:
        print 'Does not exist: {}'.format(key.key)

        continue
    except DataFile.MultipleObjectsReturned:
        print 'Multiple objects: {}'.format(key.key)

        continue

    file_name = os.path.basename(key.key)

    new_key = get_upload_path(data_file, file_name)

    print key.key
    print '  {}'.format(file_name)
    print '  {}'.format(new_key)
    print

    s3.Object(BUCKET_NAME, new_key).copy_from(
        CopySource='{0}/{1}'.format(BUCKET_NAME, key.key))

    data_file.file = new_key
    data_file.save()

    key.delete()
