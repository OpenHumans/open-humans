import json

from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase
from django.test.utils import override_settings

from .models import DataRetrievalTask, TestDataFile

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class TaskUpdateTests(SimpleTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    def setUp(self):  # noqa
        try:
            user = UserModel.objects.get(username='user1')
        except UserModel.DoesNotExist:
            user = UserModel.objects.create_user('user1', 'user1@test.com',
                                                 'user1')

        content_type = ContentType.objects.get_for_model(TestDataFile)

        self.task = DataRetrievalTask(user=user,
                                      datafile_model=content_type)

        self.task.save()

    def test_task_update_create_datafiles(self):
        data = {
            'task_data': json.dumps({
                'task_id': self.task.id,
                's3_keys': ['abc123'],
                'subtype': 'test-subtype',
            })
        }

        response = self.client.post(reverse('data-import:task-update'), data)

        self.assertEqual(response.status_code, 200)

        data_file = TestDataFile.objects.get(task=self.task)

        self.assertEqual(data_file.subtype, 'test-subtype')

    def test_task_update_task_state(self):
        states = [
            'QUEUED',
            'INITIATED',
            'SUCCESS',
            'FAILURE',
        ]

        choices = [
            DataRetrievalTask.TASK_QUEUED,
            DataRetrievalTask.TASK_INITIATED,
            DataRetrievalTask.TASK_SUCCESSFUL,
            DataRetrievalTask.TASK_FAILED,
        ]

        for state, choice in zip(states, choices):
            data = {
                'task_data': json.dumps({
                    'task_id': self.task.id,
                    'task_state': state,
                })
            }

            response = self.client.post(reverse('data-import:task-update'),
                                        data)

            self.assertEqual(response.status_code, 200)

            task = DataRetrievalTask.objects.get(id=self.task.id)

            self.assertEqual(task.status, choice)
