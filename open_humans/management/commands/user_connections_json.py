import json

from django.core.management.base import BaseCommand

from open_humans.models import Member

SOURCES = ['american_gut', 'go_viral', 'pgp', 'runkeeper', 'twenty_three_and_me', 'wildlife']


class Command(BaseCommand):
    """
    Return list of users matching a particular flag.
    """
    def add_arguments(self, parser):
        parser.add_argument('outputfile')

    def get_member_direct_sharing_sources(self, member):
        direct_sharing_sources = set()
        for sg in member.study_grants.all():
            for dr in sg.data_requests.all():
                direct_sharing_sources.add(dr.app_config.label)
        return direct_sharing_sources

    def get_member_data(self, member):
        member_data = {}
        retrievals = member.user.dataretrievaltask_set.grouped_recent()
        # App labels from the flattened list of all granted data requsets.
        direct_sharing_sources = self.get_member_direct_sharing_sources(member)
        for source in SOURCES:
            is_connected, has_files, direct_sharing, is_public = (
                False, False, False, False)
            userdata = getattr(member.user, source)
            if userdata.is_connected:
                is_connected = True
            if source in direct_sharing_sources:
                direct_sharing = True
            if is_connected and source in retrievals:
                if retrievals[source].data_files:
                    has_files = True
                if retrievals[source].is_public:
                    is_public = True
            member_data[source] = {
                'is_connected': is_connected,
                'has_files': has_files,
                'shared_directly': direct_sharing,
                'is_public': is_public,
            }
            member_data['date_joined'] = member.user.date_joined.strftime(
                '%Y%m%dT%H%M%SZ')
            member_data['email_verified'] = member.primary_email.verified
            member_data['public_data_participant'] = (
                member.public_data_participant.enrolled)
        return member_data

    def get_members_data(self):
        data = {}
        for member in Member.objects.all():
            if member.user.username == 'api-administrator':
                continue
            data[member.user.username] = self.get_member_data(member)
        return data

    def handle(self, *args, **options):
        data = self.get_members_data()
        with open(options['outputfile'], 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)
