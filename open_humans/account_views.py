from urllib.parse import unquote_plus

from django.contrib import messages as django_messages
from django.contrib.auth import logout, get_user_model
from django.shortcuts import redirect
from django.urls import resolve, reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView

from allauth.account.app_settings import (EMAIL_VERIFICATION, FORMS,
                                          LOGIN_ON_PASSWORD_RESET)
from allauth.account.forms import default_token_generator
from allauth.account.utils import (complete_signup,
                                   passthrough_next_redirect_url,
                                   perform_login,
                                   url_str_to_user_pk,
                                   user_email,
                                   user_username)
from allauth.account.models import EmailAddress
from allauth.account.views import (AjaxCapableProcessFormViewMixin,
                                   ConfirmEmailView as AllauthConfirmEmailView,
                                   LoginView as AllauthLoginView,
                                   EmailView as AllauthEmailView,
                                   PasswordChangeView as AllauthPasswordChangeView,
                                   PasswordResetView as AllauthPasswordResetView,
                                   SignupView as AllauthSignupView,
                                   _ajax_response)
from allauth.utils import get_form_class

from common.mixins import PrivateMixin
from common.utils import get_redirect_url
from private_sharing.models import OnSiteDataRequestProject

from .forms import (MemberChangeEmailForm,
                    MemberLoginForm,
                    MemberSignupForm,
                    ResetPasswordForm,
                    ChangePasswordForm,
                    PasswordResetForm)
from .models import Member


class MemberLoginView(AllauthLoginView):
    """
    A version of account's LoginView that requires the User to be a Member.
    """

    form_class = MemberLoginForm

    @property
    def join_on_site(self):
        next_url = self.request.GET.get('next')

        if next_url:
            try:
                match = resolve(unquote_plus(next_url))
            except:  # pylint: disable=bare-except
                return

            if match.url_name == 'join-on-site':
                return OnSiteDataRequestProject.objects.get(
                    slug=match.kwargs['slug'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

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

    def post(self, request, *args, **kwargs):
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
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance
        self.user = form.save(self.request)

        member = Member(user=self.user)
        member.newsletter = form.data.get('newsletter', 'off') == 'on'
        member.allow_user_messages = (
            form.data.get('allow_user_messages', 'off') == 'on')
        member.name = form.cleaned_data['name']
        member.save()

        try:
            return complete_signup(
                self.request, self.user,
                EMAIL_VERIFICATION,
                self.get_success_url())
        except ImmediateHttpResponse as e:
            return e.response


    def generate_username(self, form):
        """Override as Exception instead of NotImplementedError."""
        raise Exception(
            'Username must be supplied by form data.'
        )


class MemberChangeEmailView(PrivateMixin, AllauthEmailView):
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

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
           ret = self.form_valid(form)
        else:
            return self.form_invalid(form)
        return ret


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


class ResetPasswordView(FormView):
    """
    Ooops, we've done lost our password, Martha!
    """
    template_name = 'account/password_reset.html'
    form_class=ResetPasswordForm
    success_url = reverse_lazy("account_reset_password_done")

    def get_form_class(self):
        return get_form_class(FORMS,
                              'reset_password',
                              self.form_class)

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        login_url = passthrough_next_redirect_url(self.request,
                                                  reverse("account_login"),
                                                  'next')
        # NOTE: For backwards compatibility
        ret['password_reset_form'] = ret.get('form')
        # (end NOTE)
        ret.update({"login_url": login_url})
        return ret

    def post(self, request, *args, **kwargs):
        request = super().post(request, *args, **kwargs)
        return request


class PasswordResetFromKeyView(FormView):
    """
    Let's get a new password!
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
        user = self._get_user(uidb36)
        self.reset_user = user
        if user is None:
            return redirect('account-password-reset-fail')
        token = default_token_generator.check_token(user, key)
        if not token:
            return redirect('account-password-reset-fail')
        return super().dispatch(request, uidb36, key, **kwargs)

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

            perform_login(
                self.request, self.reset_user,
                email_verification=EMAIL_VERIFICATION)
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
    Change the password
    """
    template_name = 'account/password_change.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('my-member-settings')
    def form_valid(self, form):

        return super().form_valid(form)


class ConfirmEmailView(AllauthConfirmEmailView):
    """
    Subclass ConfirmEmailView to set the user email.
    """

    def post(self, *args, **kwargs):
        """
        Replace allauth's ConfirmEmailView.post because we want to do a few more
        things.
        """
        self.object = confirmation = self.get_object()
        confirm = confirmation.confirm(self.request)
        try:
            # For now, deleting additional email addresses as we only support one
            # This has the advantage that if a user wants to change back, they
            # can do so, and also reduces database clutter
            queryset = EmailAddress.objects.filter(user=confirm.user)
            queryset.exclude(email=confirm.email).all().delete()

            # Set new email to primary
            new_email = queryset.get(email=confirm.email)
            new_email.primary = True
            new_email.save()
        except AttributeError:
            pass # If someone tries to use an expired or incorrect key,
                 # let allauth's error handling handle it

        django_messages.add_message(
            self.request,
            django_messages.SUCCESS,
            'account/messages/email_confirmed.txt',
            {'email': confirmation.email_address.email})
        resp = self.login_on_confirm(confirmation)
        if resp is not None:
            return resp
        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        return redirect(redirect_url)
