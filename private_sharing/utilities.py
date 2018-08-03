import re

from common.utils import get_source_labels_and_names

from django.apps import apps

from private_sharing.models import DataRequestProject


def get_direct_sharing_sources():
    """
    Return a sorted list of (label, name) tuples representing the direct
    sharing sources.
    """
    sources = [(project.id_label, project.name)
               for project in (DataRequestProject.objects
                               .filter(approved=True)
                               .exclude(returned_data_description=''))]

    return sorted(sources, key=lambda x: x[1].lower())


def get_source_labels_and_names_including_dynamic():
    """
    Same as get_source_labels_and_names but include direct-sharing projects.
    """
    sources = get_source_labels_and_names() + get_direct_sharing_sources()

    return sorted(sources, key=lambda x: x[1].lower())


def source_to_url_slug(source):
    """
    Return url_slug for an "app" activity, or slug for "project" activity.

    "App" activities refers to activities that are apps within Open Humans,
    e.g. activities/fitbit, activities/ancestry_dna, and studies/american_gut.

    "Project" activities refers to standard on-site and OAuth2 projects
    (i.e. the DataRequestProject model).

    Returned slug should be valid input for the 'activity-management' page.
    """
    try:
        return apps.get_app_config(source).url_slug
    except AttributeError:
        return source
    except LookupError:
        match = re.match(r'direct-sharing-(?P<id>\d+)', source)

        if match:
            project = DataRequestProject.objects.get(id=int(match.group('id')))
            return project.slug
