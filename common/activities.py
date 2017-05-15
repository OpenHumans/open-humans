from __future__ import unicode_literals

import re

from collections import Counter, defaultdict
from functools import partial
from itertools import chain

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.urlresolvers import reverse

from common.utils import (app_label_to_user_data_model,
                          get_source_labels_and_configs)

from data_import.models import DataFile
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


def compose(*funcs):
    """
    A helper function for composing a chain of methods.
    """
    return lambda x: reduce(lambda v, f: f(v), reversed(funcs), x)


def get_labels(*args):
    """
    Convenience method to filter labels.
    """
    return {name: value for name, value in LABELS.items() if name in args}


def badge_counts():
    """
    Return a dictionary of badges in the form {label: count}; e.g.
    {'fitbit': 100}.
    """
    members = Member.objects.all().values('badges')
    badges = chain.from_iterable(member['badges'] for member in members)
    counts = Counter(badge.get('label') for badge in badges)

    return dict(counts.items())


def get_sources(user=None):
    """
    Create and return activity definitions for all of the activities in the
    'study' and 'activity' modules.
    """
    activities = defaultdict(dict)

    for label, source in get_source_labels_and_configs():
        user_data_model = app_label_to_user_data_model(label)
        is_connected = False

        if user:
            if hasattr(user_data_model, 'objects'):
                is_connected = user_data_model.objects.get(
                    user=user).is_connected
            elif hasattr(source, 'user_data'):
                is_connected = source.user_data(user=user).is_connected

        if hasattr(source, 'url_slug'):
            url_slug = source.url_slug
        else:
            url_slug = label

        activity = {
            'verbose_name': source.verbose_name,
            'badge': {
                'label': label,
                'name': source.verbose_name,
                'url': label + '/images/badge.png',
                'href': reverse('activity-management',
                                kwargs={'source': url_slug}),
            },
            'data_source': True,
            'labels': get_labels('data-source'),
            'leader': source.leader,
            'organization': source.organization,
            'description': source.description,
            'long_description': source.long_description,
            'data_description': source.data_description['description'],
            'in_development': bool(source.in_development),
            'active': True,
            'info_url': source.href_learn,
            'product_website': source.product_website,
            'connect_verb': source.connect_verb,
            'add_data_text': '{} {}'.format(source.connect_verb.title(),
                                            source.verbose_name),
            'add_data_url': source.href_add_data if source.href_add_data else source.href_connect,
            'url_slug': url_slug,
            'has_files': (user and DataFile.objects.for_user(user)
                          .filter(source=label).count() > 0),
            'is_connected': is_connected,
            'members': badge_counts().get(label, 0),
            'type': 'internal',
        }

        if hasattr(source, 'href_next'):
            activity['href_next'] = source.href_next

        if not (source.leader or source.organization):
            activity['organization'] = 'Open Humans'
            activity['contact_email'] = 'support@openhumans.org'

        if activity['leader'] and activity['organization']:
            activity['labels'].update(get_labels('study'))

        activities[label] = activity

    return activities


def activity_from_data_request_project(project, user=None):
    """
    Create an activity definition from the given DataRequestProject.
    """
    labels = []

    data_source = bool(project.returned_data_description)

    # a member can share with a project by sharing their username or their data
    share_data = (project.request_username_access or
                  project.request_sources_access)

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
        'description': project.short_description,
        'long_description': project.long_description,
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
        'members': badge_counts().get(project.id_label, 0),
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

    if user:
        activity['is_connected'] = project.is_joined(user)

    try:
        activity['badge'].update({
            'url': project.badge_image.url,
        })
    except ValueError:
        pass

    return activity


def data_request_project_badge(project):
    """
    Given a DataRequestProject, return that project's badge.
    """
    return activity_from_data_request_project(project)['badge']


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
    return {
        project.id_label: activity_from_data_request_project(
            project=project, user=user) for project in projs
    }


def manual_overrides(user, activities):
    """
    Apply any manual overrides (and create any activity definitions that
    weren't created by the other methods).
    """
    # TODO: move academic/non-profit to AppConfig
    for study_label in ['american_gut', 'pgp', 'mpower', 'wildlife']:
        activities[study_label]['labels'].update(
            get_labels('academic-non-profit'))

    # add custom info for public_data_sharing
    pds_description = ('Make your data a public resource! '
                       "If you join our study, you'll be able "
                       'to turn public sharing on (and off) for '
                       'individual data sources on your research '
                       'data page.')
    activities.update({
        'public_data_sharing': {
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
            'leader': 'Madeleine Ball',
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
        }
    })

    activities['data_selfie']['manage_files'] = reverse(
        'activities:data-selfie:manage')

    activities['vcf_data']['manage_files'] = reverse(
        'activities:genome-exome-data:manage-files')

    activities['ubiome']['manage_files'] = reverse(
        'activities:ubiome:manage-samples')

    return activities


def add_labels(activities):
    """
    Add 'inactive' and 'in-development' labels to any activity definitions that
    warrant them.
    """
    for _, activity in activities.items():
        if 'labels' not in activity:
            activity['labels'] = {}

        if not activity['active']:
            activity['labels'].update(get_labels('inactive'))

        if activity.get('in_development'):
            activity['labels'].update(get_labels('in-development'))

    return activities


def add_classes(activities):
    """
    Add classes to all activity definitions based on their labels, and add the
    special 'connected' class if the activity is connected.
    """
    for _, activity in activities.items():
        classes = activity['labels'].keys()

        if activity['is_connected']:
            classes.append('connected')

        activity['classes'] = ' '.join(classes)

    return activities


def add_source_names(activities):
    """
    Store the dictionary key of the activity definition inside the definition
    as the source_name; this is useful when we want the activity definitions as
    a list but still need their names.
    """
    for key in activities.keys():
        activities[key]['source_name'] = key

    return activities


def fix_linebreaks(activities):
    """
    Normalize linebreaks and spaces for all descriptive text fields.
    """
    def fix(string):
        string = re.sub(r'[\r\n]', ' ', string)
        string = re.sub(r' +', ' ', string)

        return string

    for _, activity in activities.items():
        activity['description'] = fix(activity['description'])
        activity['long_description'] = fix(activity['long_description'])

    return activities


def sort(activities):
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
    and running them through a composed set of methods.
    """
    metadata = dict(chain(get_sources(user).items(),
                          get_data_request_projects(
                              user,
                              only_approved=only_approved,
                              only_active=only_active).items()))

    metadata = compose(sort,
                       fix_linebreaks,
                       add_classes,
                       add_labels,
                       add_source_names,
                       partial(manual_overrides, user))(metadata)

    return metadata


def personalize_activities_dict(user=None, only_approved=True,
                                only_active=True):
    """
    Generate a dictionary of activities by converting the list from
    personalize_activities to a dict.
    """
    metadata = personalize_activities(
        user, only_approved=only_approved, only_active=only_active)

    return {activity['source_name']: activity for activity in metadata}
