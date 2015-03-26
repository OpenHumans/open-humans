from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings

from data_import.models import TestDataFile, TestUserData

from .models import Participant, PublicDataAccess


class PublicDataTestCase(TestCase):
    """
    Tests for handling of public data.
    """

    def setUp(self):  # noqa
        user = User.objects.create(username='test-user')

        Participant.objects.create(member=user.member, enrolled=True)

        test_user_data = TestUserData.objects.create(user=user)
        test_data_file = TestDataFile.objects.create(user_data=test_user_data)

        PublicDataAccess.objects.create(
            data_file_model=ContentType.objects.get_for_model(TestDataFile),
            data_file_id=test_data_file.id,
            is_public=True)

    def test_withdrawing_should_set_data_files_to_private(self):
        user = User.objects.get(username='test-user')

        self.assertTrue(user.member.public_data_participant.enrolled)
        self.assertTrue(user.data_files[0].public_data_access().is_public)

        user.member.public_data_participant.enrolled = False
        user.member.public_data_participant.save()

        self.assertFalse(user.member.public_data_participant.enrolled)
        self.assertFalse(user.data_files[0].public_data_access().is_public)


@override_settings(SSLIFY_DISABLE=True)
class SmokeTests(SimpleTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    def test_get_all_simple_urls(self):
        urls = [
            '/public-data/',
            '/public-data/consent/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_login_redirect(self):
        urls = [
            '/public-data/enroll-1-overview/',
            '/public-data/enroll-2-consent/',
            '/public-data/enroll-3-quiz/',
            '/public-data/toggle-sharing/',
            '/public-data/withdraw/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, '/account/login/?next={}'.format(
                url))

    def test_post_only(self):
        urls = [
            '/public-data/enroll-4-signature/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 405)
