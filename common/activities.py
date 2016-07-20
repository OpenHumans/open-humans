from collections import Counter, defaultdict
from functools import partial
from itertools import chain

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse_lazy

from common.utils import (app_label_to_user_data_model,
                          get_source_labels_and_configs)

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


def get_sources(request):
    activities = defaultdict(dict)

    for label, source in get_source_labels_and_configs():
        user_data_model = app_label_to_user_data_model(label)
        is_connected = False

        if request.user.is_authenticated():
            if hasattr(user_data_model, 'objects'):
                is_connected = user_data_model.objects.get(
                    user=request.user).is_connected
            elif hasattr(source, 'user_data'):
                is_connected = source.user_data(user=request.user).is_connected

        activity = {
            'verbose_name': source.verbose_name,
            'badge': {
                'url': label + '/images/badge.png',
                'name': source.verbose_name,
                'label': label,
            },
            'data_source': True,
            'labels': get_labels('data-source'),
            'leader': source.leader,
            'organization': source.organization,
            'description': source.description,
            'in_development': bool(source.in_development),
            'active': True,
            'info_url': source.href_learn,
            'add_data_text': source.connect_verb + ' data',
            'add_data_url': source.href_connect,
            'is_connected': is_connected,
            'members': badge_counts().get(label, 0),
            'type': 'internal',
        }

        if activity['leader'] and activity['organization']:
            activity['labels'].update(get_labels('study'))

        activities[label] = activity

    return activities


def activity_from_data_request_project(project, user=AnonymousUser()):
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
        'in_development': False,
        'active': True,
        'info_url': project.info_url,
        'add_data_text': 'share data',
        'members': badge_counts().get(project.id_label, 0),
        'has_files':
            project.projectdatafile_set.filter(user__pk=user.pk).count() > 0,
        'type': 'project',
        'badge': {
            'label': project.slug,
            'name': project.name,
            'url': 'direct-sharing/images/badge.png',
        },
    }

    if project.type == 'on-site':
        activity['join_url'] = reverse_lazy(
            'direct-sharing:join-on-site',
            kwargs={'slug': project.slug})
    else:
        activity['join_url'] = (
            project.oauth2datarequestproject.enrollment_url)

    if project.is_academic_or_nonprofit:
        activity['labels'].update(get_labels('academic-non-profit'))

    if project.is_study:
        activity['labels'].update(get_labels('study'))

    if user.is_authenticated():
        try:
            DataRequestProjectMember.objects.get(
                member=user.member,
                project=project,
                joined=True,
                authorized=True,
                revoked=False)

            activity['is_connected'] = True
        except DataRequestProjectMember.DoesNotExist:
            activity['is_connected'] = False
    else:
        activity['is_connected'] = False

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


def get_data_request_projects(request):
    return {
        project.id_label: activity_from_data_request_project(
            project=project, user=request.user)
        for project in DataRequestProject.objects.filter(
            approved=True, active=True)
    }


def manual_overrides(request, activities):
    # TODO: move academic/non-profit to AppConfig
    for study_label in ['american_gut', 'go_viral', 'pgp', 'wildlife',
                        'mpower']:
        activities[study_label]['labels'].update(
            get_labels('academic-non-profit'))

    activities['wildlife']['active'] = False

    # add custom info for public_data_sharing
    activities.update({
        'public_data_sharing': {
            'verbose_name': 'Public Data Sharing',
            'active': True,
            'badge': {
                'label': 'public_data_sharing',
                'name': 'Public Data Sharing',
                'url': 'images/public-data-sharing-badge.png',
            },
            'share_data': True,
            'labels': get_labels('share-data', 'academic-non-profit',
                                 'study'),
            'leader': 'Madeleine Ball',
            'organization': 'PersonalGenomes.org',
            'description': 'Make your data a public resource! '
                           "If you join our study, you'll be able "
                           'to turn public sharing on (and off) for '
                           'individual data sources on your research '
                           'data page.',
            'info_url': '',
            'has_files': '',
            'type': 'internal',
            'join_url': reverse_lazy('public-data:home'),
            'is_connected': (
                request.user.is_authenticated() and
                request.user.member.public_data_participant.enrolled),
            'members': badge_counts().get('public_data_sharing', 0),
        }
    })

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
def personalize_activities(request):
    metadata = dict(chain(get_sources(request).items(),
                          get_data_request_projects(request).items()))

    metadata = compose(sort,
                       add_classes,
                       add_labels,
                       add_source_names,
                       partial(manual_overrides, request))(metadata)

    return metadata


def personalize_activities_dict(request):
    metadata = personalize_activities(request)

    return {activity['source_name']: activity for activity in metadata}
