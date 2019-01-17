from itertools import groupby
from operator import attrgetter

import arrow

from django.apps import apps
from django.contrib import messages as django_messages
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from oauth2_provider.models import AccessToken

from common.activities import personalize_activities
from common.mixins import LargePanelMixin, PrivateMixin
from common.utils import get_activities, get_studies

from data_import.models import DataFile
from private_sharing.models import (DataRequestProjectMember,
                                    app_label_to_verbose_name_including_dynamic,
                                    id_label_to_project)

from .forms import (EmailUserForm,
                    MemberChangeNameForm,
                    MemberContactSettingsEditForm,
                    MemberProfileEditForm)
from .models import Member, EmailMetadata


class MemberDetailView(DetailView):
    """
    Creates a view of a member's public profile.
    """
    queryset = Member.objects.filter(user__is_active=True)
    template_name = 'member/member-detail.html'
    slug_field = 'user__username__iexact'

    def get_context_data(self, **kwargs):
        """
        Add context so login and signup return to this page.

        Returning to the page is desired because the user needs to be logged in
        to message a member from their detail page.
        """
        context = super(MemberDetailView, self).get_context_data(**kwargs)

        context.update({
            'next': reverse_lazy('member-detail',
                                 kwargs={'slug': self.object.user.username}),
        })

        return context


class MemberListView(ListView):
    """
    Creates a view listing members.
    """

    context_object_name = 'members'
    paginate_by = 50
    template_name = 'member/member-list.html'

    def get_projects(self):
        return DataRequestProjectMember.objects.select_related('project').filter(
                   visible=True, project__approved=True)

    def get_queryset(self):
        queryset = (Member.objects
                    .filter(user__is_active=True)
                    .select_related('user')
                    .exclude(user__username='api-administrator')
                    .order_by('user__username'))

        authorized_members = Q(datarequestprojectmember__authorized=True)
        not_revoked = Q(datarequestprojectmember__revoked=False)
        visible_members = Q(datarequestprojectmember__visible=True)

        if self.request.GET.get('filter'):
            activities = personalize_activities()
            filter_name = self.request.GET.get('filter')
            badge_exists = [activity for activity in activities
                            if activity['badge']['label'] == filter_name
                            or activity['source_name'] == filter_name]

            if not badge_exists:
                raise Http404()

            project = id_label_to_project(filter_name)
            project_members = Q(datarequestprojectmember__project=project)
            queryset = queryset.filter(project_members & authorized_members &
                                       visible_members & not_revoked)

        sorted_members = queryset.annotate(num_badges=Count('datarequestprojectmember__project',
                                                            filter=(authorized_members &
                                                                    not_revoked &
                                                                    visible_members
                                                            ))).order_by('-num_badges')
        return sorted_members

    def get_context_data(self, **kwargs):
        """
        Add context for sorting button.
        """
        context = super(MemberListView, self).get_context_data(**kwargs)

        activities = sorted(personalize_activities(),
                            key=lambda x: x['verbose_name'].lower())

        context.update({
            'activities': activities,
            'filter': self.request.GET.get('filter'),
        })

        return context


class MemberDashboardView(PrivateMixin, DetailView):
    """
    Creates a dashboard for the current user/member.

    The dashboard also displays their public member profile.
    """

    context_object_name = 'member'
    login_message = 'Please log in to see your account information.'
    queryset = Member.objects.all()
    template_name = 'member/my-member-dashboard.html'

    def get_object(self, queryset=None):
        return Member.objects.get(user=self.request.user)


class MemberProfileEditView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current user's public member profile.
    """

    form_class = MemberProfileEditForm
    login_message = 'Please log in to edit your profile.'
    model = Member
    template_name = 'member/my-member-profile-edit.html'
    success_url = reverse_lazy('my-member-dashboard')

    def get_object(self, queryset=None):
        return self.request.user.member


class MemberSettingsEditView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current user's member account settings.
    """

    form_class = MemberContactSettingsEditForm
    login_message = 'Please log in to edit your account settings.'
    model = Member
    template_name = 'member/my-member-settings.html'
    success_url = reverse_lazy('my-member-settings')

    def get_object(self, queryset=None):
        return self.request.user.member


class MemberChangeNameView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current member's name.
    """

    form_class = MemberChangeNameForm
    model = Member
    template_name = 'member/my-member-change-name.html'
    success_url = reverse_lazy('my-member-settings')

    def get_object(self, queryset=None):
        return self.request.user.member


class MemberSendConfirmationEmailView(PrivateMixin, RedirectView):
    """
    Send a confirmation email and redirect back to the settings page.
    """
    login_message = 'Please log in to send a confirmation email.'
    permanent = False

    def get_redirect_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']
        return reverse('my-member-settings')

    def get(self, request, *args, **kwargs):
        """
        Get the email address, send confirmation email, pop out a message.
        """
        # This was originally in dispatch(), but that was causing issues
        # with code being executed that required a logged in user.
        email_address = request.user.emailaddress_set.get(primary=True)
        email_address.send_confirmation()
        django_messages.success(request,
                                ('A confirmation email was sent to "{}".'
                                 .format(email_address.email)))
        return super().get(request, *args, **kwargs)


class MemberJoinedView(PrivateMixin, TemplateView):
    """
    Creates a view displaying the projects a member is sharing data with.
    """
    login_message = 'Please log in to see your account information.'
    template_name = 'member/my-member-joined.html'

    def get_context_data(self, **kwargs):
        context = super(MemberJoinedView, self).get_context_data(**kwargs)
        activities = personalize_activities(self.request.user,
                                            only_active=False)
        activities_sorted = sorted(activities, key=lambda x: x['verbose_name'])
        context.update({
            'activities': activities_sorted,
        })
        return context


class MemberDataView(PrivateMixin, TemplateView):
    """
    Creates a view displaying connected data sources and data files.
    """
    login_message = 'Please log in to see your account information.'
    template_name = 'member/my-member-data.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_memberships = (DataRequestProjectMember
                               .objects
                               .filter(member__user=self.request.user))
        user_data_files = DataFile.objects.for_user(self.request.user)
        project_labels = [membership.project.id_label
                          for membership in project_memberships]
        filtered_files = user_data_files.filter(source__in=project_labels)
        get_source = attrgetter('source')
        grouped_files = {g: list(f) for g, f in
                         groupby(filtered_files, key=get_source)}

        connected = project_memberships.filter(joined=True,
                                               authorized=True,
                                               revoked=False)
        disconnected = project_memberships.filter(Q(joined=False) |
                                                  Q(authorized=False) |
                                                  Q(revoked=True))
        context.update({
            'connected': connected,
            'disconnected': disconnected,
            'grouped_files': grouped_files,
        })
        return context


class MemberConnectionsView(PrivateMixin, TemplateView):
    """
    A view for a member to manage their connections.
    """
    login_message = 'Please log in to see your account information.'
    template_name = 'member/my-member-connections.html'

    def get_context_data(self, **kwargs):
        """
        Add connections to the request context.
        """
        context = super(MemberConnectionsView, self).get_context_data(
            **kwargs)

        connections = [
            item for item in self.request.user.member.connections.items()
            if apps.get_app_config(item[0]).disconnectable
        ]

        context.update({
            'connections': connections,
            'project_members':
                self.request.user.member.datarequestprojectmember_set.filter(
                    revoked=False),
        })

        return context


class MemberConnectionDeleteView(PrivateMixin, TemplateView):
    """
    Let the user delete a connection.

    TODO: Potential cleanup, appears to reference obsolete apps - MPB 2018-12
    """

    template_name = 'member/my-member-connections-delete.html'

    def get_access_tokens(self, connection):
        connections = self.request.user.member.connections

        if connection not in connections:
            raise Http404()

        access_tokens = AccessToken.objects.filter(
            user=self.request.user,
            application__name=connections[connection]['verbose_name'],
            application__user__username='api-administrator')

        return access_tokens

    def get_context_data(self, **kwargs):
        context = super(MemberConnectionDeleteView, self).get_context_data(
            **kwargs)

        connection_app = apps.get_app_config(kwargs.get('connection'))

        context.update({
            'connection_name': connection_app.verbose_name,
        })

        return context

    @staticmethod
    def add_sorry_message(request, verbose_name):
        django_messages.error(
            request,
            ("Sorry, we can't remove connections to {} at the present time."
             .format(verbose_name)))

    def get_redirect_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']
        return reverse('my-member-connections')

    def post(self, request, **kwargs):
        connection = kwargs.get('connection')
        connections = self.request.user.member.connections

        if not connection or connection not in connections:
            if 'next' in self.request.GET:
                return HttpResponseRedirect(self.get_redirect_url())

        verbose_name = app_label_to_verbose_name_including_dynamic(connection)

        if request.POST.get('remove_datafiles', 'off') == 'on':
            DataFile.objects.filter(user=self.request.user,
                                    source=connection).delete()

        if connection in [label for label, _ in get_studies()]:
            access_tokens = self.get_access_tokens(connection)
            access_tokens.delete()
        elif connection == 'runkeeper':
            django_messages.error(
                request,
                ('Sorry, RunKeeper connections must currently be removed by '
                 'visiting http://runkeeper.com/settings/apps'))
        elif connection == 'twenty_three_and_me':
            user_data = request.user.twenty_three_and_me
            user_data.genome_file.delete(save=True)

            django_messages.warning(
                request,
                ('We have deleted your original uploaded 23andMe file.'))
        elif connection in [label for label, _ in get_activities()]:
            user_data = getattr(request.user, connection)

            if hasattr(user_data, 'disconnect'):
                user_data.disconnect()

                django_messages.success(request, (
                    'We have removed your connection to {}.'.format(
                        verbose_name)))
            else:
                self.add_sorry_message(request, verbose_name)
        else:
            self.add_sorry_message(request, verbose_name)

        return HttpResponseRedirect(self.get_redirect_url())


class MemberEmailDetailView(PrivateMixin, LargePanelMixin, DetailView):
    """
    A simple form view for allowing a user to email another user.
    """
    login_message = 'Please log in to contact another member.'
    queryset = Member.objects.all()
    slug_field = 'user__username'
    template_name = 'member/member-email.html'

    def get_context_data(self, **kwargs):
        context = super(MemberEmailDetailView, self).get_context_data(**kwargs)
        context['form'] = EmailUserForm()
        return context


class MemberEmailFormView(PrivateMixin, LargePanelMixin, SingleObjectMixin,
                          FormView):
    """
    A view that lets a member send a message (via email) to another member if
    the receiving member has opted to receive messages. The sending account
    must be >48 hours old, have a verified email, and have sent less than 2
    messages in the last day and less than 5 in the last 7 days.
    """
    login_message = 'Please log in to contact another member.'
    queryset = Member.objects.all()
    slug_field = 'user__username'
    template_name = 'member/member-email.html'
    form_class = EmailUserForm

    error_too_many = """<em>Note: This form is intended for personal
    communication between members, and not for solicitation. If you would like
    to reach a larger number of members, please consider using our <a
    href="http://slackin.openhumans.org/">Slack</a> and/or creating a <a
    href="{project_url}">project</a> on the site.</em>"""

    error_account_age = """Sorry. The ability to send messages is only
    available for accounts after 48 hours."""

    error_verified_email = """Sorry. The ability to send messages requires a
    verified email."""

    error_both = """Sorry. The ability to send messages is only
    available for accounts after 48 hours, and requires a verified email."""

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(MemberEmailFormView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('member-detail',
                       kwargs={'slug': self.get_object().user.username})

    def log_error(self, error):
        django_messages.error(self.request, mark_safe(error))

        self.redirect = True

    def form_valid(self, form):
        sender = self.request.user
        receiver = self.get_object().user

        one_day_ago = arrow.utcnow().replace(days=-1).datetime
        two_days_ago = arrow.utcnow().replace(days=-2).datetime
        seven_days_ago = arrow.utcnow().replace(days=-7).datetime

        messages_last_day = EmailMetadata.objects.filter(
            sender=sender, timestamp__gt=one_day_ago).count()

        messages_last_seven_days = EmailMetadata.objects.filter(
            sender=sender, timestamp__gt=seven_days_ago).count()

        account_too_new = sender.date_joined >= two_days_ago
        email_unverified = not sender.member.primary_email.verified

        self.redirect = False

        if messages_last_day >= 2 or messages_last_seven_days >= 5:
            self.log_error(self.error_too_many.format(
                project_url=reverse_lazy('direct-sharing:overview')))
        elif account_too_new and email_unverified:
            self.log_error(self.error_both)
        elif account_too_new:
            self.log_error(self.error_account_age)
        elif email_unverified:
            self.log_error(self.error_verified_email)

        if self.redirect:
            return HttpResponseRedirect(self.get_success_url())

        if not receiver.member.allow_user_messages:
            django_messages.error(self.request,
                                  ('Sorry, {} does not accept user messages.'
                                   .format(receiver.username)))

            return HttpResponseRedirect(self.get_success_url())

        form.send_mail(sender, receiver)

        metadata = EmailMetadata(sender=sender, receiver=receiver)
        metadata.save()

        django_messages.success(self.request,
                                ('Your message was sent to {}.'
                                 .format(receiver.username)))

        return super(MemberEmailFormView, self).form_valid(form)


class MemberEmailView(View):
    """
    A view the composes a DetailView for displaying the member email form and a
    FormView for accepting the form and messaging the user.
    """

    @staticmethod
    def get(request, *args, **kwargs):
        view = MemberEmailDetailView.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        view = MemberEmailFormView.as_view()
        return view(request, *args, **kwargs)
