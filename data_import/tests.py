import json

from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from open_humans.models import Member

from .models import DataRetrievalTask, DataFile

UserModel = auth.get_user_model()


def create_user(name):
    """
    Helper to create a Django user.
    """
    try:
        user = UserModel.objects.get(username=name)
    except UserModel.DoesNotExist:
        user = UserModel.objects.create_user(
            name, '{}@test.com'.format(name), name)

    return user


@override_settings(SSLIFY_DISABLE=True)
class TaskUpdateTests(TestCase):
    """
    Tests for updating tasks.
    """

    @classmethod
    def setUpClass(cls):
        super(TaskUpdateTests, cls).setUpClass()

        user1 = create_user('user1')
        user2 = create_user('user2')

        Member.objects.get_or_create(user=user1)

        # test both verified and unverified users
        (member2, _) = Member.objects.get_or_create(user=user2)
        email = member2.primary_email

        email.verified = True
        email.save()

        cls.task1 = DataRetrievalTask(user=user1, source='pgp')
        cls.task2 = DataRetrievalTask(user=user1, source='pgp')

        cls.task3 = DataRetrievalTask(user=user2, source='pgp')
        cls.task4 = DataRetrievalTask(user=user2, source='pgp')
        cls.task5 = DataRetrievalTask(user=user2, source='go_viral')

        cls.task1.save()
        cls.task2.save()
        cls.task3.save()
        cls.task4.save()
        cls.task5.save()

    def test_for_user(self):
        user = UserModel.objects.get(username='user1')
        tasks = DataRetrievalTask.objects.for_user(user)

        self.assertEqual(len(tasks), 2)

    def test_for_user_verified(self):
        user = UserModel.objects.get(username='user2')
        tasks = DataRetrievalTask.objects.for_user(user)

        self.assertEqual(len(tasks), 3)

    def test_grouped_recent(self):
        user = UserModel.objects.get(username='user1')
        tasks = DataRetrievalTask.objects.for_user(user)
        grouped_recent = tasks.grouped_recent()

        self.assertEqual(grouped_recent, {'pgp': self.task2})

    def test_grouped_recent_verified(self):
        user = UserModel.objects.get(username='user2')
        tasks = DataRetrievalTask.objects.for_user(user)
        grouped_recent = tasks.grouped_recent()

        self.assertEqual(grouped_recent, {
            'pgp': self.task4,
            'go_viral': self.task5
        })

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

    def test_task_update_task_state_no_task_data(self):
        response = self.client.post(reverse('data-import:task-update'), {})

        self.assertEqual(response.status_code, 400)

    def test_task_update_task_state_bad_task_id(self):
        data = {
            'task_data': json.dumps({
                'task_id': -1,
            })
        }

        response = self.client.post(reverse('data-import:task-update'), data)

        # TODO: change to 400?
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'Invalid task ID!')

    def test_data_retrieval_view(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        response = self.client.post(
            reverse('studies:pgp:request-data-retrieval'))
        self.assertRedirects(response, reverse('my-member-research-data'))

    def test_data_retrieval_view_verified(self):
        login = self.client.login(username='user2', password='user2')
        self.assertEqual(login, True)

        response = self.client.post(
            reverse('studies:pgp:request-data-retrieval'))
        self.assertRedirects(response, reverse('my-member-research-data'))
