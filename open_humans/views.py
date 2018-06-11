import re

from collections import OrderedDict

import arrow

from django.apps import apps
from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import DeleteView, FormView
from django.db.models import Count, F

import feedparser

from common.activities import (activity_from_data_request_project,
                               personalize_activities,
                               personalize_activities_dict,
                               sort_activities)
from common.mixins import LargePanelMixin, NeverCacheMixin, PrivateMixin
from common.utils import querydict_from_dict
from common.views import BaseOAuth2AuthorizationView
from data_import.models import DataFile, is_public
from public_data.models import PublicDataAccess
from private_sharing.models import (ActivityFeed, DataRequestProject,
                                    FeaturedProject, DataRequestProjectMember,
                                    id_label_to_project)
from private_sharing.utilities import (
    get_source_labels_and_names_including_dynamic, source_to_url_slug)

from .forms import ActivityMessageForm
from .mixins import SourcesContextMixin
from .models import BlogPost, Member, GrantProject

User = get_user_model()
TEN_MINUTES = 60 * 10


class SourceDataFilesDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete all datafiles for a source. Note that DeleteView was
    written with a single object in mind but will happily delete a QuerySet due
    to duck-typing.
    """

    template_name = 'member/my-member-source-data-files-delete.html'
    success_url = reverse_lazy('my-member-data')

    def get_object(self, queryset=None):
        source = self.kwargs['source']
        self.source = source

        return DataFile.objects.filter(user=self.request.user, source=source)

    def get_context_data(self, **kwargs):
        """
        Add the source to the request context.
        """
        context = super(SourceDataFilesDeleteView, self).get_context_data(
            **kwargs)

        context.update({
            'source': self.kwargs['source'],
        })

        return context

    def get_success_url(self):
        """
        Direct to relevant activity page.
        """
        url_slug = source_to_url_slug(self.source)
        return reverse('activity-management', kwargs={'source': url_slug})


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """

    @staticmethod
    def get(request):  # pylint: disable=unused-argument
        raise Exception('A test exception.')


class OAuth2LoginView(LargePanelMixin, TemplateView):
    """
    Give people authorizing with us the ability to easily sign up or log in.
    """

    template_name = 'account/login-oauth2.html'

    def get_context_data(self, **kwargs):
        next_querystring = querydict_from_dict({
            'next': self.request.GET.get('next')
        }).urlencode()

        kwargs.update({
            'next_querystring': next_querystring,
            'connection': self.request.GET.get('connection'),
        })

        return super(OAuth2LoginView, self).get_context_data(**kwargs)


class PublicDataDocumentationView(TemplateView):
    """
    Add activities to the context.
    """

    template_name = 'pages/public-data-api.html'

    def get_context_data(self, **kwargs):
        context = super(PublicDataDocumentationView, self).get_context_data(
            **kwargs)
        activities = OrderedDict(
            get_source_labels_and_names_including_dynamic())

        context.update({
            'activities': activities,
        })

        return context


class AuthorizationView(BaseOAuth2AuthorizationView):
    """
    Add checks for study apps to the OAuth2 authorization view.
    """

    is_study_app = False

    @staticmethod
    def _check_study_app_request(context):
        """
        Return true if this OAuth2 request matches a study app
        """
        # NOTE: This assumes 'scopes' was overwritten by get_context_data.
        scopes = [x[0] for x in context['scopes']]

        try:
            scopes.remove('read')
            scopes.remove('write')
        except ValueError:
            return False

        if len(scopes) != 1:
            return False

        app_label = re.sub('-', '_', scopes[0])
        app = apps.get_app_config(app_label)

        if app and app.verbose_name == context['application'].name:
            return app_label

        return False

    def get_context_data(self, **kwargs):
        context = super(AuthorizationView, self).get_context_data(**kwargs)

        def scope_key(zipped_scope):
            scope, _ = zipped_scope

            # Sort 'write' second to last
            if scope == 'write':
                return 'zzy'

            # Sort 'read' last
            if scope == 'read':
                return 'zzz'

            # Sort all other scopes alphabetically
            return scope

        def scope_class(scope):
            if scope in ['read', 'write']:
                return 'info'

            return 'primary'

        zipped_scopes = zip(context['scopes'], context['scopes_descriptions'])
        zipped_scopes.sort(key=scope_key)

        context['scopes'] = [(scope, description, scope_class(scope))
                             for scope, description in zipped_scopes]

        # For custom display when it's for a study app connection.
        app_label = self._check_study_app_request(context)

        if app_label:
            self.is_study_app = True

            context['app'] = apps.get_app_config(app_label)
            context['app_label'] = app_label
            context['is_study_app'] = True
            context['scopes'] = [x for x in context['scopes']
                                 if x[0] != 'read' and x[0] != 'write']

        return context

    def get_template_names(self):
        if self.is_study_app:
            return ['oauth2_provider/finalize.html']

        return [self.template_name]


class HomeView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    View with recent activity feed, blog posts, and highlighted projects.
    """

    template_name = 'pages/home.html'

    @staticmethod
    def get_recent_blogposts():
        blogposts_cachetag = 'recent-blogposts'
        blogposts = cache.get(blogposts_cachetag)
        if blogposts:
            return blogposts

        blogfeed = feedparser.parse('https://blog.openhumans.org/feed/')
        posts = []
        for item in blogfeed['entries'][0:3]:
            try:
                post = BlogPost.objects.get(rss_id=item['id'])
            except BlogPost.DoesNotExist:
                post = BlogPost.create(rss_feed_entry=item)
            posts.append(post)
        return posts
        cache.set(blogposts_cachetag, posts, timeout=TEN_MINUTES)

    @staticmethod
    def get_recent_activity():
        recent = ActivityFeed.objects.order_by('-timestamp')[0:12]
        recent_1 = recent[:int((len(recent)+1)/2)]
        recent_2 = recent[int((len(recent)+1)/2):]
        return (recent_1, recent_2)

    def get_featured_projects(self):
        """
        Get FeaturedProjects in 'activity' data format

        Override description if one is provided.
        """
        featured_projs = FeaturedProject.objects.order_by('id')[0:3]
        highlighted = []
        activities = personalize_activities_dict(self.request.user)
        try:
            for featured in featured_projs:
                try:
                    activity = activities[featured.project.id_label]
                    if featured.description:
                        activity['commentary'] = featured.description
                    highlighted.append(activity)
                except KeyError:
                    pass
            return highlighted
        except (ValueError, TypeError):
            return []

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView,
                        self).get_context_data(*args, **kwargs)
        recent_activity_1, recent_activity_2 = self.get_recent_activity()

        context.update({
            'recent_activityfeed_1': recent_activity_1,
            'recent_activityfeed_2': recent_activity_2,
            'recent_blogposts': self.get_recent_blogposts(),
            'featured_projects': self.get_featured_projects(),
            'no_description': True,
        })

        return context


class PGPInterstitialView(PrivateMixin, TemplateView):
    """
    An interstitial view shown to PGP members with 1 or more private PGP
    datasets and no public PGP datasets.
    """

    template_name = 'pages/pgp-interstitial.html'

    def get(self, request, *args, **kwargs):
        request.user.member.seen_pgp_interstitial = True
        request.user.member.save()

        return super(PGPInterstitialView, self).get(request, *args, **kwargs)


class AddDataPageView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    View with data source activities. Never cached.
    """
    template_name = 'pages/add-data.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AddDataPageView,
                        self).get_context_data(*args, **kwargs)
        projects = DataRequestProject.objects.exclude(
            returned_data_description__isnull=True).exclude(
            returned_data_description='').filter(
            approved=True).filter(
            active=True)
        print(projects.count())
        activities = sort_activities(
            {proj.id_label: activity_from_data_request_project(
                project=proj, user=self.request.user) for proj in projects})
        context.update({
            'activities': activities
        })
        return context


class ExploreSharePageView(AddDataPageView):
    """
    View with data sharing activities. Never cached.
    """
    template_name = 'pages/explore-share.html'


class CreatePageView(TemplateView):
    """
    View about creating projects. Has current data sources in context.
    """

    template_name = 'pages/create.html'

    def get_context_data(self, **kwargs):
        """
        Update context with same source data used by the activities grid.
        """
        context = super(CreatePageView, self).get_context_data(**kwargs)
        activities = sorted(personalize_activities(self.request.user),
                            key=lambda k: k['source_name'].lower())
        sources = OrderedDict([
            (activity['source_name'], activity) for activity in activities if
            'data_source' in activity and activity['data_source']
        ])
        context.update({'sources': sources})
        return context


class ActivityManagementView(NeverCacheMixin, LargePanelMixin, TemplateView):
    """
    A 'home' view for each activity, with sections for describing the activity,
    the user's status for that activity, displaying the user's files for
    management, and providing methods to connect or disconnect the activity.
    """

    source = None
    template_name = 'member/activity-management.html'

    def get_activity(self, activities):
        def get_url_identifier(activity):
            return (activity.get('url_slug') or
                    activity.get('source_name'))

        by_url_id = {get_url_identifier(activities[a]):
                     activities[a] for a in activities}

        return by_url_id[self.kwargs['source']]

    def requesting_activities(self):
        activities = []
        for project in DataRequestProject.objects.filter(approved=True,
                                                         active=True):
            if self.activity['source_name'] in project.request_sources_access:
                if self.request.user.is_authenticated():
                    joined = project.is_joined(self.request.user)
                else:
                    joined = False

                activities.append({
                    'name': project.name,
                    'slug': project.slug,
                    'joined': joined,
                    'members': project.authorized_members,
                })
        return activities

    def requested_activities(self):
        activities = {}
        for source in self.project.request_sources_access:
            proj = id_label_to_project(source)
            if proj:
                activities[source] = activity_from_data_request_project(
                    proj, user=self.request.user)
        return activities

    def get_context_data(self, **kwargs):
        context = super(ActivityManagementView, self).get_context_data(
            **kwargs)

        try:
            self.project = DataRequestProject.objects.get(
                slug=self.kwargs['source'])
        except KeyError:
            raise Http404
        self.activity = activity_from_data_request_project(
            self.project, user=self.request.user)

        public_users = [
            pda.user for pda in
            PublicDataAccess.objects.filter(
                data_source=self.activity['source_name']).filter(
                is_public=True).annotate(user=F('participant__member__user'))]
        public_files = DataFile.objects.filter(
            source=self.activity['source_name']).exclude(
            parent_project_data_file__completed=False).distinct(
            'user').filter(user__in=public_users).count()

        requesting_activities = self.requesting_activities()
        requested_activities = self.requested_activities()
        data_is_public = False

        data_files = []
        if self.request.user.is_authenticated():
            data_files = (
                DataFile.objects.for_user(self.request.user)
                .filter(source=self.activity['source_name']))
            data_is_public = is_public(self.request.user.member,
                                       self.activity['source_name'])

        project = None
        project_member = None
        project_permissions = None
        granted_permissions = None
        permissions_changed = False
        if 'project_id' in self.activity:
            project = DataRequestProject.objects.get(
                pk=self.activity['project_id'])

            project_permissions = {
                'share_username': project.request_username_access,
                'send_messages': project.request_message_permission,
                'share_sources': project.request_sources_access,
                'all_sources': project.all_sources_access,
                'returned_data_description': project.returned_data_description,
            }
            if self.activity['is_connected']:
                project_member = project.active_user(self.request.user)
                granted_permissions = {
                    'share_username': project_member.username_shared,
                    'send_messages': project_member.message_permission,
                    'share_sources': project_member.sources_shared,
                    'all_sources': project_member.all_sources_shared,
                    'returned_data_description': project.returned_data_description,
                }
                permissions_changed = (not all([
                    granted_permissions[x] == project_permissions[x] for x
                    in ['share_username', 'send_messages', 'share_sources',
                        'all_sources']]))

        context.update({
            'activity': self.activity,
            'data_files': data_files,
            'is_public': data_is_public,
            'source': self.activity['source_name'],
            'project': project,
            'project_member': project_member,
            'project_permissions': project_permissions,
            'granted_permissions': granted_permissions,
            'permissions_changed': permissions_changed,
            'public_files': public_files,
            'requesting_activities': requesting_activities,
            'requested_activities': requested_activities,
        })

        return context


class ActivityMessageFormView(PrivateMixin, LargePanelMixin, FormView):
    """
    A view that lets a member send a message (via email) to a project they
    have joined, via project member ID.
    """
    template_name = 'member/activity-message.html'
    form_class = ActivityMessageForm

    def get_activity(self):
        try:
            project = DataRequestProject.objects.get(
                slug=self.kwargs['source'])
            return project
        except DataRequestProject.DoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect if user is not a project member that can accept messages.
        """
        self.project = self.get_activity()
        self.project_member = self.project.active_user(request.user)
        can_send = (self.project_member and
                    self.project_member.message_permission)
        if not can_send:
            django_messages.error(
                self.request,
                'Project messaging unavailable for "{}": you must be an '
                'active member that can receive messages from the '
                'project.'.format(self.project.name))
            return HttpResponseRedirect(self.get_redirect_url())
        return super(ActivityMessageFormView, self).dispatch(
            request, *args, **kwargs)

    def get_success_url(self):
        return self.get_redirect_url()

    def get_redirect_url(self):
        return reverse('activity-management',
                       kwargs={'source': self.project.slug})

    def get_context_data(self, **kwargs):
        """
        Add the project and project_member to the request context.
        """
        context = super(ActivityMessageFormView, self).get_context_data(
            **kwargs)
        context.update({
            'project': self.project,
            'project_member': self.project_member,
        })
        return context

    def form_valid(self, form):
        form.send_mail(self.project_member.project_member_id, self.project)

        django_messages.success(self.request,
                                ('Your message was sent to "{}".'
                                 .format(self.project.name)))

        return super(ActivityMessageFormView, self).form_valid(form)


class StatisticView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    Show latest statistics on signed up users/projects etc.
    """

    template_name = 'pages/statistics.html'

    @staticmethod
    def get_number_member():
        members = Member.objects.filter(user__is_active=True)
        members_with_data = members.annotate(
            datafiles_count=Count('user__datafiles')).filter(
            datafiles_count__gte=1)
        return (members.count(), members_with_data.count())

    @staticmethod
    def get_number_files():
        files = DataFile.objects.count()
        return files

    @staticmethod
    def get_number_active_approved():
        active_projects = DataRequestProject.objects.filter(approved=True,
                                                            active=True)
        return active_projects.count()

    @staticmethod
    def get_number_finished_approved():
        finished_projects = DataRequestProject.objects.filter(approved=True,
                                                              active=False)
        return finished_projects.count()

    @staticmethod
    def get_number_planned():
        planned_projects = DataRequestProject.objects.filter(approved=False,
                                                             active=True)
        return planned_projects.count()

    def get_context_data(self, *args, **kwargs):
        context = super(StatisticView,
                        self).get_context_data(*args, **kwargs)

        (members, members_with_data) = self.get_number_member()

        context.update({
            'number_members': members,
            'number_members_with_data': members_with_data,
            'number_files': self.get_number_files(),
            'active_projects': self.get_number_active_approved(),
            'finished_projects': self.get_number_finished_approved(),
            'planned_projects': self.get_number_planned(),
            'no_description': True,
        })

        return context

class GrantProjectView(NeverCacheMixin, TemplateView):
    """
    Show page of project grants.
    """
    template_name = 'pages/grant_projects.html'

    def get_context_data(self, **kwargs):
        context = super(GrantProjectView, self).get_context_data(**kwargs)
        context['grant_projects'] = GrantProject.objects.all().order_by('-grant_date')
        return context


def csrf_error(request, reason):
    """
    A custom view displayed during a CSRF error.
    """
    response = render(request, 'CSRF-error.html', context={'reason': reason})
    response.status_code = 403

    return response


def server_error(request):
    """
    A view displayed during a 500 error. Needed because we want to render our
    own 500 page.
    """
    response = render(request, '500.html')
    response.status_code = 500

    return response
