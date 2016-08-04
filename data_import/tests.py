import re

from django.conf import settings
from django.contrib import auth
from django.test import TestCase

from mock import patch

from common.utils import full_url

from .processing import start_task_for_source
from .utils import get_upload_dir_validator

UserModel = auth.get_user_model()


class DataImportTestCase(TestCase):
    """
    Tests for data import.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def setUp(self):
        self.user = UserModel.objects.get(username='beau')

    @patch('requests.post')
    def test_start_task_for_source(self, mock):
        start_task_for_source(self.user, 'go_viral')

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)

        args, kwargs = mock.call_args

        self.assertEqual(args[0],
                         '{}/go_viral/'.format(settings.DATA_PROCESSING_URL))

        task_params = kwargs['json']['task_params']

        self.assertEqual(task_params['access_token'],
                         settings.GO_VIRAL_MANAGEMENT_TOKEN)
        self.assertEqual(task_params['go_viral_id'], 'simplelogin:5')
        self.assertEqual(task_params['oh_user_id'], self.user.id)
        self.assertEqual(task_params['oh_member_id'], u'08868768')
        self.assertEqual(task_params['oh_update_url'],
                         full_url('/data-import/task-update/'))
        self.assertEqual(task_params['s3_bucket_name'],
                         settings.AWS_STORAGE_BUCKET_NAME)

        validator = get_upload_dir_validator('go_viral')

        self.assertTrue(re.match(validator, task_params['s3_key_dir']))
