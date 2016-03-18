from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.views.generic import (CreateView, DetailView, TemplateView,
                                  UpdateView)

from common.mixins import LargePanelMixin, PrivateMixin
from common.utils import get_source_labels_and_configs

from .forms import OAuth2DataRequestProjectForm, OnSiteDataRequestProjectForm
from .models import (DataRequestProject, DataRequestProjectMember,
                     OAuth2DataRequestProject, OnSiteDataRequestProject)

MAX_UNAPPROVED_MEMBERS = 10


class CoordinatorOrActiveDetailView(DetailView):
    """
    - Always let the coordinator view this page
    - Only let members view it if the project is active
    - Only let members view it if the project is not approved and less than
      MAX_UNAPPROVED_MEMBERS have joined.
    """

    @property
    def project_members(self):
        return DataRequestProjectMember.objects.filter(
            project=self.get_object(), revoked=False).count()

    def dispatch(self, *args, **kwargs):
        project = self.get_object()

        if project.coordinator == self.request.user:
            return super(CoordinatorOrActiveDetailView, self).dispatch(
                *args, **kwargs)

        if not project.active:
            raise Http404

        if (not project.approved and
                self.project_members > MAX_UNAPPROVED_MEMBERS):
            django_messages.error(self.request, (
                """Sorry, "{}" has not been approved and has exceeded the {}
                member limit for unapproved projects.""".format(
                    project.name, MAX_UNAPPROVED_MEMBERS)))

            return HttpResponseRedirect(reverse('my-member-research-data'))

        return super(CoordinatorOrActiveDetailView, self).dispatch(
            *args, **kwargs)


class OnSiteDetailView(CoordinatorOrActiveDetailView):
    """
    A base DetailView for on-site projects.
    """

    model = OnSiteDataRequestProject

    @property
    def project_member(self):
        project = self.get_object()
        member = self.request.member

        try:
            return DataRequestProjectMember.objects.get(
                project=project, member=member, revoked=False)
        except DataRequestProjectMember.DoesNotExist:
            return None

    @property
    def project_joined_by_member(self):
        return bool(self.project_member)

    @property
    def project_authorized_by_member(self):
        return self.project_member and self.project_member.authorized


class JoinOnSiteDataRequestProjectView(PrivateMixin, LargePanelMixin,
                                       OnSiteDetailView):
    """
    Display the consent form for a project.
    """

    template_name = 'private_sharing/join-on-site.html'

    def dispatch(self, *args, **kwargs):
        """
        If the member has already accepted the consent form redirect them to
        the authorize page.
        """
        if self.project_joined_by_member:
            return HttpResponseRedirect(reverse_lazy(
                'private-sharing:authorize-on-site',
                kwargs={'slug': self.get_object().slug}))

        return super(JoinOnSiteDataRequestProjectView, self).dispatch(
            *args, **kwargs)

    def post(self, request, *args, **kwargs):
        project = self.get_object()

        (project_member, _) = DataRequestProjectMember.objects.get_or_create(
            member=request.member,
            project=project,
            consent_text=project.consent_text)

        # if the user joins again after revoking the study then reset their
        # revoked and authorized status
        project_member.revoked = False
        project_member.authorized = False

        project_member.save()

        request.user.log('direct-sharing:on-site:consent', {
            'project-id': project.id
        })

        return HttpResponseRedirect(
            reverse_lazy('private-sharing:authorize-on-site',
                         kwargs={'slug': project.slug}))


class AuthorizeOnSiteDataRequestProjectView(PrivateMixin, LargePanelMixin,
                                            OnSiteDetailView):
    """
    Display the requested permissions for a project.
    """

    template_name = 'private_sharing/authorize-on-site.html'

    def dispatch(self, *args, **kwargs):
        """
        If the member hasn't already accepted the consent form redirect them to
        the consent form page.
        """
        # the opposite of the test in the join page
        if not self.project_joined_by_member:
            return HttpResponseRedirect(reverse_lazy(
                'private-sharing:join-on-site',
                kwargs={'slug': self.get_object().slug}))

        return super(AuthorizeOnSiteDataRequestProjectView, self).dispatch(
            *args, **kwargs)

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        project_member = self.project_member

        if self.request.POST.get('cancel') == 'cancel':
            project_member.delete()

            return HttpResponseRedirect(reverse('home'))

        project_member.authorized = True
        project_member.message_permission = project.request_message_permission
        project_member.username_shared = project.request_username_access
        project_member.sources_shared = project.request_sources_access

        project_member.save()

        request.user.log('direct-sharing:on-site:authorize', {
            'project-id': project.id
        })

        django_messages.success(request, (
            'You have successfully joined the project "{}".'.format(
                project.name)))

        return HttpResponseRedirect(reverse('my-member-research-data'))

    def get_context_data(self, **kwargs):
        context = super(AuthorizeOnSiteDataRequestProjectView,
                        self).get_context_data(**kwargs)

        project = self.get_object()
        connections = self.request.member.connections

        context.update({
            'project_authorized_by_member': self.project_authorized_by_member,
            'connected_sources': [
                source for source in project.request_sources_access
                if source in connections],
            'unconnected_sources': [
                source for source in project.request_sources_access
                if source not in connections],
        })

        return context


class UpdateDataRequestProjectView(PrivateMixin, LargePanelMixin, UpdateView):
    """
    Base view for creating an data request activities.
    """

    success_url = reverse_lazy('private-sharing:manage-projects')


class CreateDataRequestProjectView(PrivateMixin, LargePanelMixin, CreateView):
    """
    Base view for creating an data request activities.
    """

    success_url = reverse_lazy('private-sharing:manage-projects')

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.instance.coordinator = self.request.member

        return super(CreateDataRequestProjectView, self).form_valid(form)


class CreateOAuth2DataRequestProjectView(CreateDataRequestProjectView):
    """
    Create an OAuth2DataRequestProject.
    """

    template_name = 'private_sharing/create-project.html'
    model = OAuth2DataRequestProject
    form_class = OAuth2DataRequestProjectForm


class CreateOnSiteDataRequestProjectView(CreateDataRequestProjectView):
    """
    Create an OnSiteDataRequestProject.
    """

    template_name = 'private_sharing/create-project.html'
    model = OnSiteDataRequestProject
    form_class = OnSiteDataRequestProjectForm


class UpdateOAuth2DataRequestProjectView(UpdateDataRequestProjectView):
    """
    Update an OAuth2DataRequestProject.
    """

    template_name = 'private_sharing/update-project.html'
    model = OAuth2DataRequestProject
    form_class = OAuth2DataRequestProjectForm


class UpdateOnSiteDataRequestProjectView(UpdateDataRequestProjectView):
    """
    Update an OnSiteDataRequestProject.
    """

    template_name = 'private_sharing/update-project.html'
    model = OnSiteDataRequestProject
    form_class = OnSiteDataRequestProjectForm


class CoordinatorOnlyDetailView(DetailView):
    """
    Only let coordinators view these pages.
    """

    def dispatch(self, *args, **kwargs):
        project = self.get_object()

        if project.coordinator.user != self.request.user:
            raise Http404

        return super(CoordinatorOnlyDetailView, self).dispatch(
            *args, **kwargs)


class OAuth2DataRequestProjectDetailView(PrivateMixin,
                                         CoordinatorOnlyDetailView):
    """
    Display an OAuth2DataRequestProject.
    """

    template_name = 'private_sharing/project-detail.html'
    model = OAuth2DataRequestProject


class OnSiteDataRequestProjectDetailView(PrivateMixin,
                                         CoordinatorOnlyDetailView):
    """
    Display an OnSiteDataRequestProject.
    """

    template_name = 'private_sharing/project-detail.html'
    model = OnSiteDataRequestProject


class ManageDataRequestActivitiesView(PrivateMixin, TemplateView):
    """
    A view for listing all data request activities for the current user.
    """

    template_name = 'private_sharing/manage.html'

    def get_context_data(self, **kwargs):
        context = super(ManageDataRequestActivitiesView,
                        self).get_context_data(**kwargs)

        query = {'coordinator__user': self.request.user}

        oauth2 = OAuth2DataRequestProject.objects.filter(**query)
        onsite = OnSiteDataRequestProject.objects.filter(**query)

        context.update({
            'onsite': onsite,
            'oauth2': oauth2,
        })

        return context


class InDevelopmentView(TemplateView):
    """
    Add in-development projects to template context.
    """

    template_name = 'private_sharing/in-development.html'

    def get_context_data(self, **kwargs):
        context = super(InDevelopmentView, self).get_context_data(**kwargs)

        context.update({
            'projects': DataRequestProject.objects.filter(
                approved=False, active=True)
        })

        return context


class OverviewView(TemplateView):
    """
    Add current sources to template context.
    """

    template_name = 'private_sharing/overview.html'

    def get_context_data(self, **kwargs):
        context = super(OverviewView, self).get_context_data(**kwargs)

        context.update({
            'sources': get_source_labels_and_configs(),
        })

        return context


class ProjectLeaveView(PrivateMixin, DetailView):
    """
    Let a member remove themselves from a project.
    """

    template_name = 'private_sharing/leave-project.html'
    model = DataRequestProjectMember

    def post(self, *args, **kwargs):
        project_member = self.get_object()
        project_member.revoked = True
        project_member.authorized = False
        project_member.save()

        self.request.user.log(
            'direct-sharing:{0}:revoke'.format(
                project_member.project.type),
            {'project-id': project_member.id})

        return HttpResponseRedirect(reverse('my-member-connections'))
