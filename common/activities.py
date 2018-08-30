import re

from collections import Counter
from itertools import chain

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.urls import reverse

from private_sharing.models import DataRequestProject

from open_humans.models import Member

LABELS = {
    'share-data': {
        'name': 'Share data',
        'class': 'label-success',
    },
    'academic-non-profit': {
        'name': 'Academic/<br>Non-profit',
        'class': 'label-info'
    },
    'study': {
        'name': 'Study',
        'class': 'label-primary'
    },
    'data-source': {
        'name': 'Data source',
        'class': 'label-warning'
    },
    'inactive': {
        'name': 'Inactive',
        'class': 'label-default',
    },
    'in-development': {
        'name': 'In development',
        'class': 'label-default',
    },
}

TWO_HOURS = 2 * 60 * 60
ONE_MINUTE = 60


def fix_linebreaks(string):
    string = re.sub(r'[\r\n]', ' ', string)
    string = re.sub(r' +', ' ', string)

    return string


def get_labels(*args):
    """
    Convenience method to filter labels.
    """
    return {name: value for name, value in LABELS.items() if name in args}


def badge_counts_inner():
    """
    Return a dictionary of badges in the form {label: count}; e.g.
    {'fitbit': 100}.
    """
    members = Member.objects.filter(user__is_active=True)
    badges = []
    projects = DataRequestProject.objects.filter(approved=True, active=True)
    for project in projects:
        badges = chain.from_iterable(str('direct-sharing-{0}').format(project.id)
                                     for project in projects)
    counts = Counter(badges)

    return dict(counts.items())


def badge_counts():
    """
    Return badge counts.

    Badge counts are in the form {label: count}; e.g.
    {'fitbit': 100}. This function is a wrapper that provides
    caching for the result, to improve performance.
    """
    cache_tag = 'badge-counts'

    cached = cache.get(cache_tag)

    if cached:
        return cached

    badge_counts = badge_counts_inner()

    cache.set(cache_tag, badge_counts, ONE_MINUTE)

    return badge_counts


def activity_from_data_request_project(project, user=None):
    """
    Create an activity definition from the given DataRequestProject.
    """
    labels = []

    data_source = bool(project.returned_data_description)

    # a member can share with a project by sharing their username or their data
    share_data = (project.request_username_access or
                  project.request_sources_access or
                  project.all_sources_access)

    if data_source:
        labels.append('data-source')

    if share_data:
        labels.append('share-data')

    activity = {
        'verbose_name': project.name,
        'data_source': data_source,
        'share_data': share_data,
        'labels': get_labels(*labels),
        'leader': project.leader,
        'organization': project.organization,
        'contact_email': project.contact_email,
        'description': fix_linebreaks(project.short_description),
        'long_description': fix_linebreaks(project.long_description),
        'data_description': project.returned_data_description,
        'in_development': False,
        'is_connected': False,
        'active': project.active,
        'approved': project.approved,
        'info_url': project.info_url,
        'connect_verb': 'join' if project.type == 'on-site' else 'connect',
        'add_data_text': ('Join {}'.format(project.name) if
                          project.type == 'on-site' else
                          'Connect {}'.format(project.name)),
        'members': project.authorized_members,
        'project_id': project.id,
        'url_slug': project.slug,
        'has_files': (
            user and
            project.projectdatafile_set.filter(user__pk=user.pk).count() > 0),
        'type': 'project',
        'on_site': project.type == 'on-site',
        'badge': {
            'label': project.id_label,
            'name': project.name,
            'url': 'direct-sharing/images/badge.png',
            'href': reverse('activity-management',
                            kwargs={'source': project.slug}),
        },
        'source_name': project.id_label,
        'project': project,
    }

    if project.type == 'on-site':
        activity['join_url'] = reverse('direct-sharing:join-on-site',
                                       kwargs={'slug': project.slug})
    else:
        activity['join_url'] = (
            project.oauth2datarequestproject.enrollment_url)

    if project.is_academic_or_nonprofit:
        activity['labels'].update(get_labels('academic-non-profit'))

    if project.is_study:
        activity['labels'].update(get_labels('study'))

    if user and not user.is_anonymous:
        activity['is_connected'] = project.is_joined(user)

    try:
        activity['badge'].update({
            'url': project.badge_image.url,
        })
    except ValueError:
        pass

    classes = list(activity['labels'].keys())
    if activity['is_connected']:
        classes.append('connected')
    activity['classes'] = ' '.join(classes)

    return activity


def get_data_request_projects(user=None, only_approved=True, only_active=True):
    """
    Return a dictionary of type {id_label: activity_definition} that contains
    all DataRequestProjects.
    """
    if only_approved and only_active:
        projs = DataRequestProject.objects.filter(approved=True, active=True)
    elif only_approved:
        projs = DataRequestProject.objects.filter(approved=True)
    elif only_active:
        projs = DataRequestProject.objects.filter(active=True)
    else:
        projs = DataRequestProject.objects.all()

    output = {
            project.id_label: activity_from_data_request_project(
                project=project, user=user) for project in projs
        }

    return output


def public_data_activity(user):
    """
    Apply any manual overrides (and create any activity definitions that
    weren't created by the other methods).
    """
    # add custom info for public_data_sharing
    pds_description = ('Make your data a public resource! '
                       "If you activate this feature, you'll be able "
                       'to turn public sharing on and off for '
                       'individual data sources.')
    activity = {
        'verbose_name': 'Public Data Sharing',
        'active': True,
        'badge': {
            'label': 'public_data_sharing',
            'name': 'Public Data Sharing',
            'url': 'images/public-data-sharing-badge.png',
            'href': reverse('public-data:home'),
        },
        'share_data': True,
        'labels': get_labels('share-data', 'academic-non-profit',
                             'study'),
        'leader': 'Mad Ball',
        'organization': 'Open Humans Foundation',
        'description': pds_description,
        'long_description': pds_description,
        'info_url': '',
        'has_files': '',
        'type': 'internal',
        'connect_verb': 'join',
        'join_url': reverse('public-data:home'),
        'url_slug': None,
        'is_connected': (user and
                         user.member.public_data_participant.enrolled),
        'members': badge_counts().get('public_data_sharing', 0),
        'source_name': 'public_data_sharing',
    }

    classes = list(activity['labels'].keys())
    if activity['is_connected']:
        classes.append('connected')
    activity['classes'] = ' '.join(classes)

    return activity


def sort_activities(activities):
    """
    Sort the activity definitions.
    """
    def sort_order(value):
        """
        Sort activities by the number of connected members.
        """
        return -(value.get('members', 0) or 0)

    return sorted(activities.values(), key=sort_order)


def personalize_activities(user=None, only_approved=True, only_active=True):
    """
    A wrapper that caches activities for the case where there's no
    authenticated user. Could be extended for caching a user's activities but
    would need either a shorter expiration or a method to invalidate the cache
    for a user when they joined/disconnected an activity.

    Also note that a low value is used (two hours) because a logged out user
    will not immediately see changes to the home page if a new data request
    project is approved. A signal to invalidate the cache when projects change
    would allow a higher expiration time.
    """
    if user == AnonymousUser():
        user = None

    if not user:
        cache_tag = 'personalize-activities'
        if only_approved:
            cache_tag = cache_tag + '-approved'
        if only_active:
            cache_tag = cache_tag + '-active'

        cached = cache.get(cache_tag)

        if cached:
            return cached

        activities = personalize_activities_inner(
            user, only_approved=only_approved, only_active=only_active)

        cache.set(cache_tag, activities, timeout=TWO_HOURS)

        return activities

    return personalize_activities_inner(user, only_approved=only_approved,
                                        only_active=only_active)


def personalize_activities_inner(user, only_approved=True, only_active=True):
    """
    Generate a list of activities by getting sources and data request projects
    sorted according to number of members joined.
    """
    activities = get_data_request_projects(
        user,
        only_approved=only_approved,
        only_active=only_active)

    activities['public_data_sharing'] = public_data_activity(user)

    activities_sorted = sort_activities(activities)

    return activities_sorted


def personalize_activities_dict(user=None, only_approved=True,
                                only_active=True):
    """
    Generate a dictionary of activities by converting the list from
    personalize_activities to a dict.
    """
    metadata = personalize_activities(
        user, only_approved=only_approved, only_active=only_active)

    return {activity['source_name']: activity for activity in metadata}
