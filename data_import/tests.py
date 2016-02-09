import json

from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from open_humans.models import Member

from .models import DataRetrievalTask, DataFile

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class TaskUpdateTests(TestCase):
    """
    Tests for updating tasks.
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

        cls.task1 = DataRetrievalTask(user=user, source='pgp')
        cls.task2 = DataRetrievalTask(user=user, source='pgp')

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

        self.assertEqual(grouped_recent, {'pgp': self.task2})

    def test_task_update_create_datafiles(self):
        data = {
            'task_data': json.dumps({
                'task_id': self.task1.id,
                's3_keys': ['abc123'],
            })
        }

        response = self.client.post(reverse('data-import:task-update'), data)

        self.assertEqual(response.status_code, 200)

        data_file = DataFile.objects.get(task=self.task1)

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

        data_file = DataFile.objects.get(task=self.task2)

        self.assertEqual(data_file.file.name, 'abc123')
        self.assertEqual(data_file.tags, ['foo', 'bar'])
        self.assertEqual(data_file.description, 'Some explanation')

        file_id = DataFile.objects.filter(task=self.task2)[0].id

        url = reverse('data-import:datafile-download', kwargs={'pk': file_id})

        # an anonymouse user shouldn't be able to see the file
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        # a logged in user should
        response = self.client.get(url, follow=False)
        self.assertEqual(response.url.startswith(
            'https://{}.s3.amazonaws.com/abc123?Signature='.format(
                settings.AWS_STORAGE_BUCKET_NAME)), True)

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

    def test_data_retrieval_view(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        response = self.client.post(
            reverse('studies:pgp:request-data-retrieval'))
        self.assertRedirects(response, reverse('my-member-research-data'))
