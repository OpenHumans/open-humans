from django.core.management.base import BaseCommand

from private_sharing.models import (DataRequestProject,
                                    DataRequestProjectMember,
                                    GrantedSourcesAccess,
                                    RequestSourcesAccess,
                                    id_label_to_project)

def convert_old_source_label(source):
    """
    Converts old source label to new project
    """
    if source == 'go_viral':
        requested_project = DataRequestProject.objects.get(id=24)
    elif source == 'illumina_uyg':
        requested_project = DataRequestProject.objects.get(id=131)
    print('Updating old-style source {source} to {new_proj}'
          .format(source=source, new_proj=requested_project.name))
    return requested_project



class Command(BaseCommand):
    """
    A command for populating RequestSourcesAccess from
    DataRequestProject.request_sources_access
    """

    help = ('Populate RequestSourcesAccess from '
            'DataRequestProject.request_sources_access.')

    def handle(self, *args, **options):
        """
        When run, this reads through all projects requesting sources and
        replicates them in the new table, RequestSourcesAccess.
        """

        projects = DataRequestProject.objects.exclude(
            request_sources_access=[])

        for project in projects:
            for source in project.request_sources_access:
                requested_project = id_label_to_project(source)
                if requested_project == None:
                    requested_project = convert_old_source_label(source)
                existing = RequestSourcesAccess.objects.filter(
                    requested_project=requested_project).filter(
                        requesting_project=project).filter(active=True)
                if not existing.exists():
                    requested_source = RequestSourcesAccess(
                        requesting_project=project,
                        requested_project=requested_project,
                        active=True)
                    requested_source.save()

        project_members = DataRequestProjectMember.objects.exclude(
            sources_shared=[])
        for project_member in project_members:
            for source in project_member.sources_shared:
                requested_project = id_label_to_project(source)
                if requested_project == None:
                    requested_project = convert_old_source_label(source)
                existing = (GrantedSourcesAccess.objects.filter(
                    requested_project=requested_project).filter(
                        requesting_project=project_member.project)
                            .filter(project_member=project_member)
                            .filter(active=True))
                if not existing.exists():
                    granted_sources = GrantedSourcesAccess(
                        requesting_project=project_member.project,
                        requested_project=requested_project,
                        project_member=project_member,
                        active=True)
                    granted_sources.save()
