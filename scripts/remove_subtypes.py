#!/usr/bin/env python

from env_tools import apply_env

apply_env()

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

django.setup()

from activities.runkeeper.models import DataFile

data_files = DataFile.objects.all()

for data_file in data_files:
    # some instances don't have a subtype set but we can infer it from the
    # filename
    if not data_file.subtype:
        if 'activity-data' in data_file.file.name:
            data_file.subtype = 'activity-data'
        elif 'sleep-data' in data_file.file.name:
            data_file.subtype = 'sleep-data'
        elif 'social-data' in data_file.file.name:
            data_file.subtype = 'social-data'
        else:
            raise ValueError('invalid filename')

        data_file.save()

    print 'processing {}'.format(data_file.subtype)

    # if it's sleep-data or social-data then delete it
    if data_file.subtype in ['sleep-data', 'social-data']:
        print 'deleting {} for {}'.format(data_file.subtype,
                                          data_file.user_data.user.username)

        data_file.delete()
