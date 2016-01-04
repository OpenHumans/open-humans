import json

from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from open_humans.models import Member
from studies.pgp.models import DataFile as PgpDataFile

from .models import DataRetrievalTask, TestDataFile
from .utils import app_name_to_content_type

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class TaskUpdateTests(TestCase):
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

        cls.task1 = DataRetrievalTask(user=user,
                                      datafile_model=content_type)
        cls.task2 = DataRetrievalTask(user=user,
                                      datafile_model=content_type)

        cls.task1.save()
        cls.task2.save()

    def test_for_user(self):
        user = UserModel.objects.get(username='user1')
        tasks = DataRetrievalTask.objects.for_user(user)

        self.assertEqual(len(tasks), 2)

    def test_grouped_recent(self):
        user = UserModel.objects.get(username='user1')
        tasks = DataRetrievalTask.objects.for_user(user)
        grouped_recent = tasks.grouped_recent()

        self.assertEqual(grouped_recent, {'data_import': self.task2})

    def test_task_update_create_datafiles(self):
        data = {
            'task_data': json.dumps({
                'task_id': self.task1.id,
                's3_keys': ['abc123'],
            })
        }

        response = self.client.post(reverse('data-import:task-update'), data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.task1.is_public, False)

        data_file = TestDataFile.objects.get(task=self.task1)

        self.assertEqual(data_file.file.name, 'abc123')

    def test_task_update_create_datafiles_with_metadata(self):
        data = {
            'task_data': json.dumps({
                'task_id': self.task2.id,
                'data_files': [
                    {
                        's3_key': 'abc123',
                        'metadata': {
                            'description': 'Some explanation',
                            'tags': ['foo', 'bar'],
                            'original_filename': 'orig-file-name.tsv.bz2',
                            'source_url':
                                'http://example.com/source/orig-file.tsv.bz2'
                        },
                    },
                ],
            })
        }

        response = self.client.post(reverse('data-import:task-update'), data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.task2.is_public, False)

        data_file = TestDataFile.objects.get(task=self.task2)

        self.assertEqual(data_file.file.name, 'abc123')
        self.assertEqual(data_file.tags, ['foo', 'bar'])
        self.assertEqual(data_file.description, 'Some explanation')

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
                    'task_id': self.task1.id,
                    'task_state': state,
                })
            }

            response = self.client.post(reverse('data-import:task-update'),
                                        data)

            self.assertEqual(response.status_code, 200)

            task = DataRetrievalTask.objects.get(id=self.task1.id)

            self.assertEqual(task.status, choice)
            self.assertEqual(task.is_public, False)

    def test_app_name_to_content_type(self):
        model, _ = app_name_to_content_type('pgp')

        self.assertEqual(model, PgpDataFile)
