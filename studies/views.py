from account.views import (ConfirmEmailView as AccountConfirmEmailView,
                           LoginView as AccountLoginView,
                           SignupView as AccountSignupView)

from django.apps import apps
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from rest_framework.generics import (ListCreateAPIView, RetrieveAPIView,
                                     RetrieveUpdateAPIView,
                                     RetrieveUpdateDestroyAPIView)

from common.mixins import LargePanelMixin, NeverCacheMixin, PrivateMixin
from common.permissions import HasValidToken

from open_humans.views import AuthorizationView

from .forms import (ResearcherAddRoleForm,
                    ResearcherLoginForm,
                    ResearcherSignupForm,
                    StudyDataRequestForm)
from .models import Researcher, Study, StudyGrant


class UserDataMixin(object):
    """
    A mixin that handles getting the UserData for a given user and access
    token.
    """

    def get_user_data_related_name(self):
        """
        Return the related_name of the UserData model in relation to the User
        model, e.g. american_gut, go_viral, pgp
        """
        return self.user_data_model.user.field.related_query_name()

    def get_user_data(self):
        """
        A helper function to retrieve the given study's UserData model that
        corresponds to the request user.
        """
        # We get the UserData object this way because if we try to do it via a
        # filter the object will not be automatically created (it's an
        # AutoOneToOneField and so is only created when accessed like
        # `user.american_gut`)
        return getattr(self.request.user, self.get_user_data_related_name())

    def get_user_data_queryset(self):
        """
        A helper function to retrieve the given study's UserData model as a
        pre-filtered queryset that corresponds to the request user.
        """
        # HACK: A side effect of this call is that the UserData object will be
        # created if it doesn't exist... Which is useful for the next line,
        # which filters by it.
        self.get_user_data()

        return self.user_data_model.objects.filter(user=self.request.user)

    # TODO: Add scope permissions here?
    def get_object(self):
        """
        Get an object from its `pk`.
        """
        filters = {}

        # There's only one UserData for a given user so we don't need to filter
        # for it. We set its lookup_field to None for this reason.
        if self.lookup_field:
            filters[self.lookup_field] = self.kwargs[self.lookup_field]

        obj = get_object_or_404(self.get_queryset(), **filters)

        self.check_object_permissions(self.request, obj)

        return obj

    def perform_create(self, serializer):
        """
        perform_create is called when models are saved. We add in the user_data
        here so that on model creation it's set correctly.
        """
        serializer.save(user_data=self.get_user_data())


class UserDataDetailView(NeverCacheMixin, UserDataMixin,
                         RetrieveUpdateAPIView):
    """
    A read-only detail view for a study's UserData object.
    """
    lookup_field = None
    permission_classes = (HasValidToken,)


class StudyDetailView(NeverCacheMixin, UserDataMixin,
                      RetrieveUpdateDestroyAPIView):
    """
    A detail view that can be GET, PUT, DELETEd.
    """
    permission_classes = (HasValidToken,)


class RetrieveStudyDetailView(NeverCacheMixin, UserDataMixin, RetrieveAPIView):
    """
    A detail view that can be GET.
    """
    permission_classes = (HasValidToken,)


class StudyListView(NeverCacheMixin, UserDataMixin, ListCreateAPIView):
    """
    A list view that can be GET or POSTed.
    """
    permission_classes = (HasValidToken,)


class ResearcherLoginView(AccountLoginView):
    """
    A version of account's LoginView that requires the User to be a Researcher.
    """
    template_name = 'research/account/login.html'
    form_class = ResearcherLoginForm

    def get_success_url(self, fallback_url=None, **kwargs):
        """
        Override default (settings.ACCOUNT_LOGIN_REDIRECT_URL) with 'home'.
        """
        if fallback_url is None:
            fallback_url = reverse('home')
        return super(ResearcherLoginView, self).get_success_url(
            fallback_url=fallback_url, **kwargs)

    def form_valid(self, form):
        """
        Check if email confirmation or account approval are needed.
        """
        # Check for email confirmation, then check for approval.
        # Store blocked user's username as a session variable;
        # this session cookie should last until user's browser closes.
        email_address = form.user.emailaddress_set.get(primary=True)
        if not email_address.verified or not form.user.researcher.approved:
            self.request.session.set_expiry(0)
            self.request.session['blocked-user'] = form.user.username
            if not email_address.verified:
                return redirect('account_confirmation_needed')
            return redirect('account_approval_needed')

        return super(ResearcherLoginView, self).form_valid(form)


class ResearcherSignupView(AccountSignupView):
    """
    Creates a view for signing up for a Researcher account.

    This is a subclass of accounts' SignupView using our form customizations,
    including addition of a name field and a TOU confirmation checkbox.
    """
    template_name = 'research/account/signup.html'
    template_name_email_confirmation_sent = ('research/account/'
                                             'email_confirmation_sent.html')
    form_class = ResearcherSignupForm

    def create_account(self, form):
        """
        Override to add Researcher creation to account creation process.
        """
        account = super(ResearcherSignupView, self).create_account(form)

        # We only create Researchers from this view. This account won't have a
        # Member account and can't log in as a Member on the main site.
        researcher = Researcher(user=account.user)
        researcher.save()

        account.user.researcher.name = form.cleaned_data['name']
        account.user.researcher.save()

        return account

    def generate_username(self, form):
        """
        Override as StandardError instead of NotImplementedError.
        """
        raise StandardError(
            'Username must be supplied by form data.'
        )

    def get_success_url(self, fallback_url=None, **kwargs):
        """
        Override default (settings.ACCOUNT_SIGNUP_REDIRECT_URL) with 'home'.
        """
        if fallback_url is None:
            fallback_url = reverse('home')
        return super(ResearcherSignupView, self).get_success_url(
            fallback_url=fallback_url, **kwargs)


class ResearcherConfirmEmailView(AccountConfirmEmailView):
    """
    Subclass to override defaults.
    """
    def get_template_names(self):
        """
        Override default templates.
        """
        return {
            'GET': ['research/account/email_confirm.html'],
            'POST': ['research/account/email_confirmed.html'],
        }[self.request.method]

    def get_redirect_url(self):
        """
        Override defaults (settings.ACCOUNT_EMAIL_CONFIRMATION_*_URL) to 'home'
        """
        if self.request.user.is_authenticated():
            return reverse('home')


def _get_user_data(username):
    user = get_user_model().objects.get(username=username)
    email_address = user.emailaddress_set.get(primary=True)
    return user, email_address


class ResearcherConfirmationNeededView(TemplateView):
    """
    Prompt email confirmation after refusing Researcher login.
    """
    template_name = 'research/account/confirmation_needed.html'

    def get(self, request):
        # Check Researcher isn't logged in and email isn't confirmed.
        if (request.user.is_authenticated() or
                'blocked-user' not in request.session):
            return redirect('home')
        user, email_address = _get_user_data(request.session['blocked-user'])
        if email_address.verified:
            return redirect('home')

        # Prompt email confirmation.
        return self.render_to_response({'user': user,
                                        'email_address': email_address})

    @staticmethod
    def post(request):
        # Send confirmation.
        _, email_addr = _get_user_data(request.session.pop('blocked-user'))

        email_addr.send_confirmation(site=get_current_site(request))

        django_messages.success(
            request,
            'A confirmation email was sent to "%s".' % email_addr.email)

        # Redirect to home page.
        return redirect('home')


class ResearcherApprovalNeededView(TemplateView):
    """
    Prompt request for approval after refusing Researcher login.
    """
    template_name = 'research/account/approval_needed.html'

    def get(self, request):
        # Check Researcher isn't logged in and isn't approved.
        if (request.user.is_authenticated() or
                'blocked-user' not in request.session):
            return redirect('home')
        user, email_address = _get_user_data(request.session['blocked-user'])
        if user.researcher.approved:
            return redirect('home')

        # Prompt request for account approval.
        return self.render_to_response({'user': user,
                                        'email_address': email_address})


class ResearcherAddRoleView(FormView):
    """
    A form for adding the researcher role to a user.
    """

    template_name = 'research/account/add_researcher_role.html'
    form_class = ResearcherAddRoleForm

    def form_valid(self, form):
        researcher = Researcher(user=form.user, name=form.cleaned_data['name'])
        researcher.save()
        django_messages.success(
            self.request,
            'A Researcher role has been added for %s.' % form.user.username)
        return super(ResearcherAddRoleView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home')


class StudyDataRequestView(FormView):
    """
    Allow study administrators to specify data requirements.
    """

    template_name = 'research/studies/edit-data-requirement.html'
    form_class = StudyDataRequestForm

    # TODO:
    # - don't allow editing of studies the study administrator doesn't own


class StudyGrantView(PrivateMixin, LargePanelMixin, DetailView):
    """
    A DetailView that displays a study's data requests and allows the user to
    approve them.
    """

    model = Study
    template_name = 'studies/grant.html'

    def get_context_data(self, **kwargs):
        context = (super(StudyGrantView, self)
                   .get_context_data(**kwargs))

        study = self.get_object()

        required_apps = set(d.app_name
                            for d in study.data_requests.all()
                            if d.required)

        required_grants = set(d.app_key
                              for d in study.data_requests.all()
                              if d.required)

        all_connected = all(d.app_key in self.request.user.member.connections
                            for d in study.data_requests.all())

        required_connected = all(key in self.request.user.member.connections
                                 for key in required_grants)

        context.update({
            'all_connected': all_connected,
            'required_apps': required_apps,
            'required_connected': required_connected,
        })

        return context

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs):
        study = self.get_object()

        study_grant, _ = StudyGrant.objects.get_or_create(
            member=request.user.member,
            study=study)

        study_grant.save()

        approved_requests = []

        for data_request in study.data_requests.all():
            if (data_request.required or
                    data_request.request_key in request.POST):
                approved_requests.append(data_request)

        study_grant.data_requests = approved_requests
        study_grant.save()

        return redirect('studies:complete', slug=study.slug)


class StudyGrantCompletionView(PrivateMixin, LargePanelMixin, DetailView):
    """
    A DetailView that displays the completion page for a study conection flow.
    """

    model = Study
    template_name = 'studies/grant-complete.html'


class StudyAuthorizationView(AuthorizationView, LargePanelMixin):
    """
    An interstitial authorization view for studies. After the user approves the
    study's access to data the user will be redirected to the StudyGrantView.
    """

    template_name = 'studies/authorize.html'

    def get_context_data(self, **kwargs):
        context = (super(StudyAuthorizationView, self)
                   .get_context_data(**kwargs))

        context.update({
            'scopes': ['read'],
        })

        return context


class StudyConnectionReturnView(PrivateMixin, TemplateView):
    """
    Handles redirecting the user to the research data page (and can be
    overridden by individual studies).
    """
    template_name = 'studies/connect-return.html'

    def get_context_data(self, **kwargs):
        context = super(StudyConnectionReturnView, self).get_context_data(
            **kwargs)

        context['study_verbose_name'] = self.study_verbose_name
        context['badge_url'] = self.badge_url
        context['return_url'] = self.return_url

        return context

    def get(self, request, *args, **kwargs):
        """
        If user started on OH, go to research data. Otherwise offer choice.

        If an origin parameter exists and indicates the user started on the
        connection process on Open Humans, then send them to their research
        data page.

        Otherwise, assume the user started on the study site. Offer the option
        to return, or to continue to Open Humans.
        """
        redirect_url = reverse('my-member-research-data')
        origin = request.GET.get('origin', '')

        if origin == 'open-humans':
            return HttpResponseRedirect(redirect_url)

        # Search apps to find the study app specified by the URL 'name' slug.
        study_name = kwargs.pop('name').replace('-', '_')
        app_configs = apps.get_app_configs()

        self.study_verbose_name = ''

        for app_config in app_configs:
            if app_config.name.endswith(study_name):
                self.study_verbose_name = app_config.verbose_name
                self.badge_url = '{}/images/badge.png'.format(study_name)
                self.return_url = getattr(request.user,
                                          app_config.label).href_connect

        if self.study_verbose_name:
            return super(StudyConnectionReturnView, self).get(
                request, *args, **kwargs)
        else:
            # TODO: Unexpected! Report error, URL should match study app.
            return HttpResponseRedirect(redirect_url)
