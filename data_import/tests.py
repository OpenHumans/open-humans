from django.conf import settings
from django.contrib import auth
from django.test import TestCase

from mock import patch

from .processing import start_task

UserModel = auth.get_user_model()


class DataImportTestCase(TestCase):
    """
    Tests for data import.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def setUp(self):
        self.user = UserModel.objects.get(username='beau')

    @patch('requests.post')
    def test_start_task(self, mock):
        start_task(self.user, 'go_viral')

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)

        args, kwargs = mock.call_args

        self.assertEqual(args[0],
                         '{}/go_viral/'.format(settings.DATA_PROCESSING_URL))

        self.assertEqual(kwargs['params']['key'], settings.PRE_SHARED_KEY)
        self.assertEqual(kwargs['json']['oh_user_id'], self.user.id)
