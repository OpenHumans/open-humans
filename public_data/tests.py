from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from data_import.models import TestDataFile, TestUserData

from .models import Participant, PublicDataStatus


class PublicDataTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test-user')

        Participant.objects.create(member=user.member, enrolled=True)

        test_user_data = TestUserData.objects.create(user=user)
        test_data_file = TestDataFile.objects.create(user_data=test_user_data)

        PublicDataStatus.objects.create(
            data_file_model=ContentType.objects.get_for_model(TestDataFile),
            data_file_id=test_data_file.id,
            is_public=True)

    def test_withdrawing_should_set_data_files_to_private(self):
        user = User.objects.get(username='test-user')

        self.assertTrue(user.member.public_data_participant.enrolled)
        self.assertTrue(user.data_files[0].public_data_status().is_public)

        user.member.public_data_participant.enrolled = False
        user.member.public_data_participant.save()

        self.assertFalse(user.member.public_data_participant.enrolled)
        self.assertFalse(user.data_files[0].public_data_status().is_public)
