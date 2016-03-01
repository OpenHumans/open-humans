from operator import attrgetter

from django.apps import apps
from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from oauth2_provider.models import AccessToken

from activities.data_selfie.models import DataSelfieDataFile
from common.mixins import LargePanelMixin, PrivateMixin
from common.utils import app_label_to_verbose_name, get_activities, get_studies

from data_import.models import DataFile, DataRetrievalTask

from .forms import (EmailUserForm,
                    MemberChangeNameForm,
                    MemberContactSettingsEditForm,
                    MemberDataSelfieUpdateViewForm,
                    MemberProfileEditForm)
from .models import Member, EmailMetadata


class MemberDetailView(DetailView):
    """
    Creates a view of a member's public profile.
    """
    queryset = Member.enriched.all()
    template_name = 'member/member-detail.html'
    slug_field = 'user__username'

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

    def get_queryset(self):
        if self.request.GET.get('sort') == 'username':
            return (Member.objects
                    .select_related('user')
                    .exclude(user__username='api-administrator')
                    .order_by('user__username'))

        # First sort by name and username
        sorted_members = sorted(Member.objects
                                .select_related('user')
                                .exclude(user__username='api-administrator'),
                                key=attrgetter('user.username'))

        # Then sort by number of badges
        sorted_members = sorted(sorted_members,
                                key=lambda m: len(m.badges),
                                reverse=True)

        return sorted_members

    def get_context_data(self, **kwargs):
        """
        Add context for sorting button.
        """
        context = super(MemberListView, self).get_context_data(**kwargs)

        if self.request.GET.get('sort') == 'username':
            sort_direction = 'connections'
            sort_description = 'by number of connections'
        else:
            sort_direction = 'username'
            sort_description = 'by username'

        context.update({
            'sort_direction': sort_direction,
            'sort_description': sort_description,
        })

        return context


class MemberDashboardView(PrivateMixin, DetailView):
    """
    Creates a dashboard for the current user/member.

    The dashboard also displays their public member profile.
    """
    context_object_name = 'member'
    queryset = Member.enriched.all()
    template_name = 'member/my-member-dashboard.html'

    def get_object(self, queryset=None):
        return Member.enriched.get(user=self.request.user)


class MemberProfileEditView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current user's public member profile.
    """
    form_class = MemberProfileEditForm
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
    permanent = False
    url = reverse_lazy('my-member-settings')

    def get_redirect_url(self, *args, **kwargs):
        redirect_field_name = self.request.GET.get('redirect_field_name',
                                                   'next')
        next_url = self.request.GET.get(redirect_field_name, self.url)
        return next_url

    def dispatch(self, request, *args, **kwargs):
        email_address = request.user.emailaddress_set.get(primary=True)
        email_address.send_confirmation()
        django_messages.success(request,
                                ('A confirmation email was sent to "{}".'
                                 .format(email_address.email)))
        return super(MemberSendConfirmationEmailView, self).dispatch(
            request, *args, **kwargs)


class MemberResearchDataView(PrivateMixin, ListView):
    """
    Creates a view for displaying and importing research/activity datasets.
    """
    template_name = 'member/my-member-research-data.html'
    context_object_name = 'data_retrieval_tasks'

    def get_queryset(self):
        return (DataRetrievalTask.objects
                .for_user(self.request.user)
                .grouped_recent())

    def get_context_data(self, **kwargs):
        """
        Add DataRetrievalTask to the request context.
        """
        context = super(MemberResearchDataView, self).get_context_data(
            **kwargs)

        data_selfie_files = (DataFile.objects.filter(user=self.request.user,
                                                     source='data_selfie'))

        context['DataRetrievalTask'] = DataRetrievalTask
        context['data_selfie_files'] = data_selfie_files
        context['user_activities'] = [{
            'user_data': getattr(self.request.user, label),
            'template': app_config.connection_template,
        } for label, app_config in get_activities()]

        return context


class MemberDataSelfieView(PrivateMixin, ListView):
    """
    Creates a view for displaying data selfie files.
    """
    template_name = 'member/my-member-data-selfie.html'
    context_object_name = 'data_files'

    def get_queryset(self):
        return DataSelfieDataFile.objects.filter(user=self.request.user)


class MemberDataSelfieAcknowledgeView(PrivateMixin, View):
    """
    Let the user acknowledge that they've seen the data selfie modal.
    """
    @staticmethod
    def post(request):
        user_data = request.user.data_selfie
        user_data.seen_page = True
        user_data.save()

        return HttpResponse('')


class MemberDataSelfieUpdateView(PrivateMixin, UpdateView):
    """
    Creates a view for displaying data selfie files.
    """
    form_class = MemberDataSelfieUpdateViewForm
    model = DataFile
    template_name = 'member/my-member-data-selfie-edit.html'
    success_url = reverse_lazy('my-member-data-selfie')

    def get_object(self, queryset=None):
        return (DataSelfieDataFile.objects.get(id=self.kwargs['data_file'],
                                               user=self.request.user))


class MemberConnectionsView(PrivateMixin, TemplateView):
    """
    A view for a member to manage their connections.
    """

    template_name = 'member/my-member-connections.html'

    def get_context_data(self, **kwargs):
        """
        Add connections and study_grants to the request context.
        """
        context = super(MemberConnectionsView, self).get_context_data(
            **kwargs)

        connections = [
            item for item in self.request.user.member.connections.items()
            if apps.get_app_config(item[0]).disconnectable
        ]

        context.update({
            'connections': connections,
            'study_grants': self.request.user.member.study_grants.all(),
        })

        return context


class MemberConnectionDeleteView(PrivateMixin, TemplateView):
    """
    Let the user delete a connection.
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

    def post(self, request, **kwargs):
        connection = kwargs.get('connection')
        connections = self.request.user.member.connections

        if not connection or connection not in connections:
            return HttpResponseRedirect(reverse('my-member-connections'))

        verbose_name = app_label_to_verbose_name(connection)

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
                ('We have deleted your original uploaded 23andMe file. You '
                 'will need to remove your processed files separately on your '
                 'research data management page.'))
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

        return HttpResponseRedirect(reverse('my-member-connections'))


class MemberEmailView(PrivateMixin, LargePanelMixin, DetailView, FormView):
    """
    A simple form view for allowing a user to email another user.
    """
    form_class = EmailUserForm
    queryset = Member.enriched.all()
    slug_field = 'user__username'
    template_name = 'member/member-email.html'

    def get_success_url(self):
        return reverse('member-detail',
                       kwargs={'slug': self.get_object().user.username})

    def form_valid(self, form):
        sender = self.request.user
        receiver = self.get_object().user

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

        return super(MemberEmailView, self).form_valid(form)
