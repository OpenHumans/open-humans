import json
import itertools

from django.core.management.base import BaseCommand

from common.utils import get_source_labels
from data_import.models import DataFile, is_public
from open_humans.models import Member


def flatten(l):
    """
    Flatten a 2-dimensional list.
    """
    return list(itertools.chain.from_iterable(l))


class Command(BaseCommand):
    """
    Return list of users matching a particular flag.
    """
    def add_arguments(self, parser):
        parser.add_argument('outputfile')

    @staticmethod
    def get_member_direct_sharing_sources(member):
        data_requests = flatten([study_grant.data_requests.all()
                                 for study_grant in member.study_grants.all()])

        return {data_request.app_config.label
                for data_request in data_requests}

    def get_member_data(self, member):
        member_data = {}
        retrievals = member.user.dataretrievaltask_set.grouped_recent()

        # App labels from the flattened list of all granted data requsets.
        direct_sharing_sources = self.get_member_direct_sharing_sources(member)

        for source in get_source_labels():

            userdata = getattr(member.user, source)
            is_connected = bool(userdata.is_connected)

            has_files, source_is_public = (False, False)

            # Check for files.
            if source == 'data_selfie':
                files = DataFile.objects.filter(user=member.user,
                                                source='data_selfie')
                if files:
                    has_files = True
            else:
                if is_connected and source in retrievals:
                    has_files = retrievals[source].datafiles.count() > 0

            # Check public sharing.
            if is_connected:
                source_is_public = is_public(member, source)

            # Check for direct sharing.
            direct_sharing = source in direct_sharing_sources

            member_data[source] = {
                'is_connected': is_connected,
                'has_files': has_files,
                'shared_directly': direct_sharing,
                'is_public': source_is_public,
            }

        member_data['date_joined'] = member.user.date_joined.strftime(
            '%Y%m%dT%H%M%SZ')

        if member.primary_email:
            member_data['email_verified'] = member.primary_email.verified
        else:
            member_data['email_verified'] = False

        member_data['public_data_participant'] = (
            member.public_data_participant.enrolled)

        return member_data

    def get_members_data(self):
        members = Member.enriched.all().exclude(
            user__username='api-administrator')
        return {member.user.username: self.get_member_data(member)
                for member in members}

    def handle(self, *args, **options):
        data = self.get_members_data()

        with open(options['outputfile'], 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)
