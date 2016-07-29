import json

from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from common.testing import get_or_create_user
from open_humans.models import Member

from .models import DataFile

UserModel = auth.get_user_model()

#
# TODO_DATAFILE_MANAGEMENT
