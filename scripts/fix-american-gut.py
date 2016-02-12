#!/usr/bin/env python

from env_tools import apply_env

apply_env()

import django
import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

django.setup()

from studies.american_gut.models import UserData

with open('survey-ids.json') as mappings_file:
    mappings = json.load(mappings_file)

user_data = UserData.objects.all()


def translate(survey_id):
    if survey_id in mappings:
        return mappings[survey_id]

    return survey_id

for ud in user_data:
    new_survey_ids = [translate(s) for s in ud.survey_ids]

    if new_survey_ids != ud.survey_ids:
        ud.data['surveyIds'] = new_survey_ids
        ud.save()
