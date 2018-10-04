from urllib.parse import unquote_plus

from django.contrib import messages as django_messages
from django.contrib.auth import logout, get_user_model
from django.shortcuts import redirect
from django.urls import resolve, reverse, reverse_lazy
from django.utils.http import is_safe_url
from django.views.generic.edit import DeleteView, FormView

import allauth.account.app_settings as allauth_settings
from allauth.account.forms import (AddEmailForm as AllauthAddEmailForm,
                                   default_token_generator)
from allauth.account.utils import (perform_login,
                                   url_str_to_user_pk)
from allauth.account.models import EmailAddress
from allauth.account.views import (ConfirmEmailView as AllauthConfirmEmailView,
                                   LoginView as AllauthLoginView,
                                   EmailView as AllauthEmailView,
                                   PasswordChangeView as AllauthPasswordChangeView,
                                   PasswordResetView as AllauthPasswordResetView,
                                   SignupView as AllauthSignupView)
from allauth.socialaccount.views import(SignupView as AllauthSocialSignupView)

from common.mixins import PrivateMixin
from private_sharing.models import OnSiteDataRequestProject

from .forms import (ChangePasswordForm,
                    MemberLoginForm,
                    MemberSignupForm,
                    PasswordResetForm,
                    ResetPasswordForm,
                    SocialSignupForm)
from .models import User, Member


class MemberLoginView(AllauthLoginView):
    """
    Add redirects to allauth's loginview
    """

    form_class = MemberLoginForm

    def post(self, request, *args, **kwargs):
        """
        Since we are now encoding the redirect url, we wind up short circuiting
        django's HttpResponseRedirect, which doesn't quite handle it correctly.
        """
        ret = super().post(self, request, *args, **kwargs)
        try:
            return redirect(unquote_plus(ret.url))
        except AttributeError:
            return ret


class MemberSignupView(AllauthSignupView):
    """
    Creates a view for signing up for a Member account.

    This is a subclass of accounts' SignupView using our form customizations,
    including addition of a name field and a TOU confirmation checkbox.
    """

    form_class = MemberSignupForm

    def form_valid(self, form):
        """
        By assigning the User to a property on the view, we allow subclasses
        of SignupView to access the newly created User instance

        Also extract next url and decode it as per LoginView
        """
        ret = super().form_valid(form)

        member = Member(user=self.user)
        member.newsletter = form.data.get('newsletter', 'off') == 'on'
        member.allow_user_messages = (
            form.data.get('allow_user_messages', 'off') == 'on')
        member.name = form.cleaned_data['name']
        member.save()

        try:
            return redirect(unquote_plus(ret.url))
        except AttributeError:
            return ret


    def generate_username(self, form):
        """Override as Exception instead of NotImplementedError."""
        raise Exception(
            'Username must be supplied by form data.'
        )


class MemberChangeEmailView(PrivateMixin, AllauthEmailView):
    """
    Creates a view for the current user to change their email.

    Uses our own email change template.
    """

    form_class = AllauthAddEmailForm
    template_name = 'member/my-member-change-email.html'
    success_url = reverse_lazy('my-member-settings')
    messages = {
        'settings_updated': {
            'level': django_messages.SUCCESS,
            'text': 'Email address updated and confirmation email sent.'
        },
    }

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        email = str(form.data['email'])
        emailaddress = EmailAddress.objects.filter(email=email)
        if emailaddress.count() == 1:
            if emailaddress.first().primary == False:
                emailaddress.delete()

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


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


class ResetPasswordView(AllauthPasswordResetView):
    """
    Ooops, we've done lost our password, Martha!  Subclasses Allauth's
    view to use our template and use our own form which preserves the
    next url for when the password reset process is complete.
    """
    template_name = 'account/password_reset.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy("account_reset_password_done")


class PasswordResetFromKeyView(FormView):
    """
    Let's get a new password!  Allauth tries to be fancy with ajax,
    but we don't really use ajax ourselves, so this view does the work
    of getting the key and calling the check functions directly.
    """
    template_name = 'account/password_reset_token.html'
    form_class = PasswordResetForm

    def _get_user(self, uidb36):
        User = get_user_model()
        try:
            pk = url_str_to_user_pk(uidb36)
            return User.objects.get(pk=pk)
        except (ValueError, User.DoesNotExist):
            return None

    def dispatch(self, request, uidb36, key, **kwargs):
        self.request = request
        self.key = key
        self.reset_user = self._get_user(uidb36)
        if self.reset_user is None:
            return redirect('account-password-reset-fail')
        token = default_token_generator.check_token(self.reset_user, key)
        if not token:
            return redirect('account-password-reset-fail')
        ret = super().dispatch(request, uidb36, key, **kwargs)
        return ret

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['action_url'] = reverse(
            'account_reset_password_from_key',
            kwargs={'uidb36': self.kwargs['uidb36'],
                    'key': self.kwargs['key']})
        return ret

    def change_password(self, password):
        user = self.reset_user
        user.set_password(password)
        user.save()
        return user

    def form_valid(self, form):
        if form.is_valid():
            self.change_password(form.clean_password())

            if allauth_settings.LOGIN_ON_PASSWORD_RESET:
                perform_login(
                    self.request, self.reset_user,
                    email_verification=allauth_settings.EMAIL_VERIFICATION)
            member = Member.objects.get(user=self.reset_user)
            next_url = member.password_reset_redirect
            member.password_reset_redirect = '' # Clear redirect from db
            member.save()
            messages = {
                'settings_updated': {
                    'level': django_messages.SUCCESS,
                    'text': 'Password successfully reset.'},}
            return redirect(unquote_plus(next_url))


class PasswordChangeView(AllauthPasswordChangeView):
    """
    Change the password, subclass allauth to use our own template
    """
    template_name = 'account/password_change.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('my-member-settings')


class ConfirmEmailView(AllauthConfirmEmailView):
    """
    Subclass ConfirmEmailView to set the user email, in addition to
    deleting spare emails, as we only support a single email per
    account.
    """

    def post(self, *args, **kwargs):
        """
        Replace allauth's ConfirmEmailView.post because we want to do a few more
        things.
        """
        ret = super().post(*args, **kwargs)
        new_email = self.object.email_address.email
        user = self.object.email_address.user
        try:
            # For now, deleting additional email addresses as we only support one
            # This has the advantage that if a user wants to change back, they
            # can do so, and also reduces database clutter
            queryset = EmailAddress.objects.filter(user=user)
            queryset.exclude(email=new_email).all().delete()

            # Set new email to primary
            email = queryset.get(email=new_email)
            email.primary = True
            email.save()

            auth_user = User.objects.get(pk=user.pk)
            auth_user.email = new_email
            auth_user.save()

        except AttributeError:
            pass # If someone tries to use an expired or incorrect key,
                 # let allauth's error handling handle it

        return ret


class SocialSignupView(AllauthSocialSignupView):
    """
    Subclass Allauth's socialaccount.views.SignupView to specificy our template.
    """
    form_class = SocialSignupForm
    success_url = reverse_lazy('home')
    template_name = 'socialaccount/signup.html'


    def form_valid(self, form):
        if form.is_valid():
            print('asdf')
