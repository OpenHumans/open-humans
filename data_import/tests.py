import json

from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase
from django.test.utils import override_settings

from open_humans.models import Member
from studies.pgp.models import DataFile as PgpDataFile

from .models import DataRetrievalTask, TestDataFile
from .utils import app_name_to_content_type

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class TaskUpdateTests(SimpleTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    @classmethod
    def setUpClass(cls):
        super(TaskUpdateTests, cls).setUpClass()

        try:
            user = UserModel.objects.get(username='user1')
        except UserModel.DoesNotExist:
            user = UserModel.objects.create_user('user1', 'user1@test.com',
                                                 'user1')
        Member.objects.get_or_create(user=user)

        content_type = ContentType.objects.get_for_model(TestDataFile)

        cls.task = DataRetrievalTask(user=user,
                                     datafile_model=content_type)

        cls.task.save()

    def test_for_user(self):
        user = UserModel.objects.get(username='user1')
        tasks = DataRetrievalTask.objects.for_user(user)

        self.assertEqual(len(tasks), 1)

    def test_grouped_recent(self):
        user = UserModel.objects.get(username='user1')
        tasks = DataRetrievalTask.objects.for_user(user)
        grouped_recent = tasks.grouped_recent()

        self.assertEqual(grouped_recent, {'data_import': self.task})

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
        self.assertEqual(self.task.is_public, False)

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
            DataRetrievalTask.TASK_SUCCEEDED,
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
            self.assertEqual(task.is_public, False)

    def test_app_name_to_content_type(self):
        model, _ = app_name_to_content_type('pgp')

        self.assertEqual(model, PgpDataFile)
