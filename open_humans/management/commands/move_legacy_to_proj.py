from itertools import groupby

from django.apps import apps
from django.core.management.base import BaseCommand

from data_import.models import DataFile
from open_humans.models import Member
from private_sharing.models import (
    DataRequestProject, DataRequestProjectMember, ProjectDataFile)


class Command(BaseCommand):
    """
    Transfer a legacy source to an OH-operated project.

    Creates a corresponding project membership, and modifies associated
    DataFile objects to be associated with this project.

    ID and slug of the target project are both requested in input to reduce
    the chance of accidentally transfering to an incorrect project.

    This function is written generically because it may be re-used in the
    future, but it needs to be tested with each app! self.ALLOWED_APPS reflects
    this; modify this only after testing.
    """

    ALLOWED_APPS = ['twenty_three_and_me']
    help = 'Transfer a legacy source to a project'

    def add_arguments(self, parser):
        parser.add_argument('--legacy', type=str,
                            help='label of legacy source to be transferred')
        parser.add_argument('--proj-id', type=str,
                            help='ID of project to transfer to')
        parser.add_argument('--proj-slug', type=str,
                            help='Slug of project to transfer to')
        parser.add_argument('--userdata-field-clean',
                            help='Set this legacy UserData field to None')
        parser.add_argument('--user', type=str,
                            help='Transfer just a specific user by username')
        parser.add_argument('--all-users', action='store_true',
                            help='Run for all users')

    def handle(self, *args, **options):
        proj_id = options['proj_id']
        proj_slug = options['proj_slug']
        legacy_source = options['legacy']
        userdata_field_clean = options['userdata_field_clean']
        username = options['user']
        all_users = options['all_users']

        if username and all_users:
            raise ValueError('Either specify a user or all-users, not both!')

        project = self._get_proj(
            proj_id=proj_id, proj_slug=proj_slug)
        legacy_config, legacy_files_by_uid = self._get_legacy(
            legacy_source=legacy_source)

        if username:
            uid_list = [Member.objects.get(user__username=username).user.id]
        elif all_users:
            uid_list = sorted(legacy_files_by_uid.keys())
        else:
            uid_list = []

        for uid in uid_list:
            project_member = self._create_projmember(project=project, uid=uid)
            print('Transferring {}...'.format(
                project_member.member.user.username))
            legacy_userdata = legacy_config.models[
                'userdata'].objects.get(user__id=uid)
            if userdata_field_clean:
                setattr(legacy_userdata, userdata_field_clean, None)
                legacy_userdata.save()
            for df in legacy_files_by_uid[uid]:
                df.source = project.id_label
                df.save()
                self._create_projdatafile(df, project_member)
            print('Transferred {}'.format(project_member.member.user.username))

    def _get_proj(self, proj_id, proj_slug):
        project = DataRequestProject.objects.get(id=proj_id)
        if proj_slug != project.slug:
            raise ValueError("Project ID ({}) and slug ({}) don't "
                             'match!'.format(proj_id, proj_slug))
        return project

    def _get_legacy(self, legacy_source):
        if legacy_source not in self.ALLOWED_APPS:
            raise ValueError('App label "{}" not in ALLOWED_APPS!'.format(
                legacy_source))

        legacy_config = apps.get_app_config(legacy_source)

        legacy_files_by_uid = {
            key: [r for r in result] for key, result in groupby(
                DataFile.objects.filter(source=legacy_source).current(),
                key=lambda x: x.user.id)}

        return legacy_config, legacy_files_by_uid

    def _create_projmember(self, project, uid):
        member = Member.objects.get(user__id=uid)
        project_member, _ = DataRequestProjectMember.objects.get_or_create(
            member=member,
            project=project)
        if project.type == 'oauth2':
            project_member.joined = True

        project_member.authorized = True
        project_member.revoked = False
        project_member.message_permission = project.request_message_permission
        project_member.username_shared = project.request_username_access
        project_member.sources_shared = project.request_sources_access
        project_member.all_sources_shared = project.all_sources_access
        project_member.save()

        return project_member

    def _create_projdatafile(self, df, proj_member):
        pdf = ProjectDataFile(
            completed=True,
            parent=df,
            direct_sharing_project=proj_member.project,
            user=proj_member.member.user,
            source=df.source,
            archived=df.archived,
            created=df.created,
            metadata=df.metadata,
            file=df.file)
        pdf.save()
        return pdf
