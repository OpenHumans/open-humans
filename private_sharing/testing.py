from cStringIO import StringIO

from common.testing import SmokeTestCase

from .models import DataRequestProjectMember


class DirectSharingMixin(object):
    """
    Mixins for both types of direct sharing tests.
    """

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]

    @staticmethod
    def setUp():
        """
        Delete all ProjectMembers so tests don't rely on each others' state.
        """
        DataRequestProjectMember.objects.all().delete()

    def update_member(self, joined, authorized):
        # first delete the ProjectMember
        try:
            project_member = DataRequestProjectMember.objects.get(
                member=self.member1,
                project=self.member1_project)

            project_member.delete()
        except DataRequestProjectMember.DoesNotExist:
            pass

        # then re-create it
        project_member = DataRequestProjectMember(
            member=self.member1,
            project=self.member1_project,
            joined=joined,
            authorized=authorized,
            sources_shared=self.member1_project.request_sources_access,
            username_shared=self.member1_project.request_username_access,
            message_permission=self.member1_project.request_message_permission)

        project_member.save()

        return project_member

    def test_file_upload(self):
        member = self.update_member(joined=True, authorized=True)

        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.member1_project.master_access_token),
            data={
                'project_member_id': member.project_member_id,
                'metadata': ('{"description": "Test description... ", '
                             '"tags": ["tag 1", "tag 2", "tag 3"]}'),
                'data_file': StringIO('just testing...'),
            })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(response.json(), 'errors')

    def test_file_upload_bad_metadata(self):
        member = self.update_member(joined=True, authorized=True)

        # tags not an array
        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.member1_project.master_access_token),
            data={
                'project_member_id': member.project_member_id,
                'metadata': ('{"description": "Test description... ", '
                             '"tags": "tag 1, tag 2, tag 3"}'),
                'data_file': StringIO('just testing...'),
            })

        self.assertIn('errors', response.json())
        self.assertEqual(response.status_code, 400)

        # tags missing
        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.member1_project.master_access_token),
            data={
                'project_member_id': member.project_member_id,
                'metadata': '{"description": "Test description... "}',
                'data_file': StringIO('just testing...'),
            })

        self.assertIn('errors', response.json())
        self.assertEqual(response.status_code, 400)

        # description missing
        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.member1_project.master_access_token),
            data={
                'project_member_id': member.project_member_id,
                'metadata': '{"tags": ["tag 1", "tag 2", "tag 3"]}',
                'data_file': StringIO('just testing...'),
            })

        self.assertIn('errors', response.json())
        self.assertEqual(response.status_code, 400)

        # data_file missing
        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.member1_project.master_access_token),
            data={
                'project_member_id': member.project_member_id,
                'metadata': ('{"description": "Test description... ", '
                             '"tags": ["tag 1", "tag 2", "tag 3"]}'),
                'tags': '["tag 1", "tag 2", "tag 3"]',
            })

        self.assertIn('errors', response.json())
        self.assertEqual(response.status_code, 400)

        # project_member_id missing
        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.member1_project.master_access_token),
            data={
                'metadata': ('{"description": "Test description... ", '
                             '"tags": ["tag 1", "tag 2", "tag 3"]}'),
                'data_file': StringIO('just testing...'),
            })

        self.assertIn('errors', response.json())
        self.assertEqual(response.status_code, 400)
