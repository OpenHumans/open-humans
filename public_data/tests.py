from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase

from common.testing import SmokeTestCase
from open_humans.models import Member
from private_sharing.models import DataRequestProject, DataRequestProjectMember

from .models import Participant, PublicDataAccess

UserModel = get_user_model()


class PublicDataTestCase(TransactionTestCase):
    """
    Tests for handling of public data.
    """

    def setUp(self):  # noqa
        user = UserModel.objects.create(username="test-user")
        member = Member.objects.create(user=user)
        project = DataRequestProject.objects.create(
            name="Example project",
            id=1,
            is_study=False,
            request_username_access=False,
            coordinator=member,
            is_academic_or_nonprofit=False,
        )

        drpm = DataRequestProjectMember(member=member, project=project)
        drpm.save()
        participant = Participant.objects.create(member=member, enrolled=True)

        PublicDataAccess.objects.create(
            participant=participant, project_membership=drpm, is_public=True
        )

    def test_withdrawing_should_set_data_files_to_private(self):
        user = UserModel.objects.get(username="test-user")

        self.assertTrue(user.member.public_data_participant.enrolled)
        self.assertTrue(
            user.member.public_data_participant.publicdataaccess_set.all()[0].is_public
        )

        user.member.public_data_participant.enrolled = False
        user.member.public_data_participant.save()

        self.assertFalse(user.member.public_data_participant.enrolled)
        self.assertFalse(
            user.member.public_data_participant.publicdataaccess_set.all()[0].is_public
        )


class SmokeTests(SmokeTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    authenticated_or_anonymous_urls = ["/public-data/"]

    authenticated_urls = [
        "/public-data/activate-1-overview/",
        "/public-data/activate-2-information/",
        "/public-data/toggle-sharing/",
        "/public-data/deactivate/",
    ]

    post_only_urls = [
        "/public-data/activate-3-quiz/",
        "/public-data/activate-4-complete/",
    ]
