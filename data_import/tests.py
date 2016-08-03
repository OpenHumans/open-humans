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


class DataImportTestCase(TestCase):
    """
    Tests for data import.
    """

    def setUp(self):
        self.user = UserModel.objects.create(username='test-user')
        self.member = Member.objects.create(user=self.user)

    def test_start_task_for_source(self):
        pass

    def test_task_signal(self):
        pass
