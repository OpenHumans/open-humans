from collections import Counter, defaultdict
from functools import partial
from itertools import chain

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse

from common.utils import (app_label_to_user_data_model,
                          get_source_labels_and_configs)

from data_import.models import DataFile
from private_sharing.models import DataRequestProject, DataRequestProjectMember

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
    members = Member.objects.all().values('badges')
    badges = chain.from_iterable(member['badges'] for member in members)
    counts = Counter(badge.get('label') for badge in badges)

    return dict(counts.items())


def get_sources(user=None):
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
            'add_data_url': source.href_connect,
            'url_slug': url_slug,
            'has_files': (user and DataFile.objects.for_user(user)
                          .filter(source=label).count() > 0),
            'is_connected': is_connected,
            'members': badge_counts().get(label, 0),
            'type': 'internal',
        }

        if not (source.leader or source.organization):
            activity['organization'] = 'Open Humans'
            activity['contact_email'] = 'support@openhumans.org'

        if activity['leader'] and activity['organization']:
            activity['labels'].update(get_labels('study'))

        activities[label] = activity

    return activities


def activity_from_data_request_project(project, user=None):
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
        'active': True,
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
            'label': project.slug,
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


def get_data_request_projects(user=None):
    return {
        project.id_label: activity_from_data_request_project(
            project=project, user=user)
        for project in DataRequestProject.objects.filter(
            approved=True, active=True)
    }


def manual_overrides(user, activities):
    # TODO: move academic/non-profit to AppConfig
    for study_label in ['american_gut', 'go_viral', 'pgp', 'wildlife',
                        'mpower']:
        activities[study_label]['labels'].update(
            get_labels('academic-non-profit'))

    activities['wildlife']['active'] = False

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
            'organization': 'PersonalGenomes.org',
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

    activities['data_selfie']['badge']['href'] = reverse(
        'activities:data-selfie:manage')

    activities['vcf_data']['badge']['href'] = reverse(
        'activities:genome-exome-data:manage-files')

    return activities


def add_labels(activities):
    for _, activity in activities.items():
        if 'labels' not in activity:
            activity['labels'] = {}

        if not activity['active']:
            activity['labels'].update(get_labels('inactive'))

        if activity.get('in_development'):
            activity['labels'].update(get_labels('in-development'))

    return activities


def add_classes(activities):
    for _, activity in activities.items():
        classes = activity['labels'].keys()

        if activity['is_connected']:
            classes.append('connected')

        activity['classes'] = ' '.join(classes)

    return activities


def add_source_names(activities):
    for key in activities.keys():
        activities[key]['source_name'] = key

    return activities


def sort(activities):
    def sort_order(value):
        CUSTOM_ORDERS = {
            'American Gut': -1000003,
            'GoViral': -1000002,
            'Harvard Personal Genome Project': -1000001,
        }

        return CUSTOM_ORDERS.get(value['verbose_name'],
                                 -(value.get('members', 0) or 0))

    return sorted(activities.values(), key=sort_order)


# TODO: possible to cache the metadata if the request passed is anonymous
# since it will always be the same
def personalize_activities(user=None):
    if user == AnonymousUser():
        user = None

    metadata = dict(chain(get_sources(user).items(),
                          get_data_request_projects(user).items()))

    metadata = compose(sort,
                       add_classes,
                       add_labels,
                       add_source_names,
                       partial(manual_overrides, user))(metadata)

    return metadata


def personalize_activities_dict(user=None):
    metadata = personalize_activities(user)

    return {activity['source_name']: activity for activity in metadata}
