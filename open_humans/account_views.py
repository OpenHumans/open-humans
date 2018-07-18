from django.contrib import messages as django_messages
from django.contrib.auth import logout
from django.core.urlresolvers import resolve, reverse_lazy
from django.views.generic.edit import DeleteView

from account.views import (LoginView as AccountLoginView,
                           SettingsView as AccountSettingsView,
                           SignupView as AccountSignupView)

from common.mixins import PrivateMixin
from private_sharing.models import OnSiteDataRequestProject

from .forms import MemberChangeEmailForm, MemberLoginForm, MemberSignupForm
from .models import Member


class MemberLoginView(AccountLoginView):
    """
    A version of account's LoginView that requires the User to be a Member.
    """

    form_class = MemberLoginForm

    @property
    def join_on_site(self):
        next_url = self.request.GET.get('next')

        if next_url:
            try:
                match = resolve(next_url)
            except:  # pylint: disable=bare-except
                return

            if match.url_name == 'join-on-site':
                return OnSiteDataRequestProject.objects.get(
                    slug=match.kwargs['slug'])

    def get_context_data(self, *args, **kwargs):
        context = super(MemberLoginView, self).get_context_data(
            *args, **kwargs)

        if self.join_on_site:
            context.update({
                'project': self.join_on_site,
            })

        return context

    def get_template_names(self):
        """
        If the `next` parameter is the 'join-on-site' view then use a different
        template with additional information about joining.
        """
        if self.join_on_site:
            return ['private_sharing/join-on-site-login.html']

        return [self.template_name]


class MemberSignupView(AccountSignupView):
    """
    Creates a view for signing up for a Member account.

    This is a subclass of accounts' SignupView using our form customizations,
    including addition of a name field and a TOU confirmation checkbox.
    """

    form_class = MemberSignupForm

    def create_account(self, form):
        account = super(MemberSignupView, self).create_account(form)

        # We only create Members from this view, which means that if a User has
        # a Member then they've signed up to Open Humans and are a participant.
        member = Member(user=account.user)

        member.newsletter = form.data.get('newsletter', 'off') == 'on'
        member.allow_user_messages = (
            form.data.get('allow_user_messages', 'off') == 'on')

        member.name = form.cleaned_data['name']

        member.save()

        # this may not be necessary, but we do return the account object here
        # so if it's consumed by anything that uses the member we'll want it to
        # have the up to date version that includes the user's preferences and
        # name
        account.user.member = member

        return account

    def generate_username(self, form):
        """Override as Exception instead of NotImplementedError."""
        raise Exception(
            'Username must be supplied by form data.'
        )


class MemberChangeEmailView(PrivateMixin, AccountSettingsView):
    """
    Creates a view for the current user to change their email.

    This is an email-only subclass of account's SettingsView.
    """

    form_class = MemberChangeEmailForm
    template_name = 'member/my-member-change-email.html'
    success_url = reverse_lazy('my-member-settings')
    messages = {
        'settings_updated': {
            'level': django_messages.SUCCESS,
            'text': 'Email address updated and confirmation email sent.'
        },
    }

    def get_success_url(self, *args, **kwargs):
        kwargs.update(
            {'fallback_url': reverse_lazy('my-member-settings')})
        return super(MemberChangeEmailView, self).get_success_url(
            *args, **kwargs)


class UserDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete their account.
    """

    context_object_name = 'user'
    template_name = 'account/delete.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        response = super(UserDeleteView, self).delete(request, *args, **kwargs)

        # Log the user out prior to deleting them so that they don't appear
        # logged in when they're redirected to the homepage.
        logout(request)

        return response

    def get_object(self, queryset=None):
        return self.request.user
