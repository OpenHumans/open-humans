from captcha.fields import ReCaptchaField

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from allauth.account.forms import (AddEmailForm as AllauthAddEmailForm,
                                   ChangePasswordForm as AllauthChangePasswordForm,
                                   LoginForm as AllauthLoginForm,
                                   ResetPasswordForm as AllauthResetPasswordForm,
                                   SignupForm as AllauthSignupForm)

from common.utils import get_redirect_url
from .models import Member

def _clean_password(child_class, self_instance, password_field_name):
    """
    A custom password validator that enforces a minimum length.
    """
    min_len = settings.ACCOUNT_PASSWORD_MIN_LEN
    # Also use parent method if django-user-accounts ever implements it.
    parent_clean_password = getattr(super(child_class, self_instance),
                                    'clean_' + password_field_name, None)
    if parent_clean_password:
        parent_clean_password()
    if len(self_instance.cleaned_data[password_field_name]) < min_len:
        raise forms.ValidationError('Password should be at least ' +
                                    '%d characters long.' % min_len)
    return self_instance.cleaned_data[password_field_name]


class MemberLoginForm(AllauthLoginForm):
    """
    A subclass of django-allauth's form that checks user is a Member.
    """

    authentication_fail_message = ("Your password didn't match the " +
                                   'username or email you provided.')

    def clean(self):
        """Check that the user is a Member."""
        cleaned_data = super().clean()
        if self._errors:
            return
        if self.user:

            try:
                Member.objects.get(user=self.user)
            except Member.DoesNotExist:
                raise forms.ValidationError(
                    "This account doesn't have a Member role.")

        return cleaned_data

    def get_success_url(self):
        return get_redirect_url(self.request)


class MemberSignupForm(AllauthSignupForm):
    """
    A subclass of django-allauth's SignupForm with additions.

    A `terms` field is added for the Terms of Use checkbox, a `name` field
    is added to store a Member's username, and additional validation is
    added for passwords to impose a minimum length.
    """

    name = forms.CharField(max_length=30)
    terms = forms.BooleanField()

    class Meta:  # noqa: D101
        fields = '__all__'

    def clean(self):
        super().clean()

        if 'terms' not in self.cleaned_data:
            self.add_error('terms', _('You must accept our terms of service.'))

        return self.cleaned_data

    def clean_password(self):
        return _clean_password(AllauthSignupForm, self, 'password')


class ChangePasswordForm(AllauthChangePasswordForm):
    """
    A subclass of account's ChangePasswordForm that checks password length.
    """

    def clean_password_new(self):
        return _clean_password(ChangePasswordForm, self, 'password_new')


class PasswordResetForm(forms.Form):
    """
    A subclass of account's PasswordResetTokenForm that checks password length.
    """

    password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        label="New Password (again)",
        widget=forms.PasswordInput(render_value=False))

    def clean(self):
        super().clean()
        if self._errors:
            return

        if 'password' in self.cleaned_data \
           and 'password_confirm' in self.cleaned_data:
            if self.cleaned_data['password'] \
               != self.cleaned_data['password_confirm']:
                self.add_error(
                    'password_confirm',
                    'You must type the same password each time.')

        return self.cleaned_data


    def clean_password(self):
        return _clean_password(PasswordResetForm, self, 'password')


class MemberProfileEditForm(forms.ModelForm):
    """
    A form for editing a member's profile information.
    """

    class Meta:  # noqa: D101
        model = Member
        fields = ('profile_image', 'about_me',)


class MemberContactSettingsEditForm(forms.ModelForm):
    """
    A form for editing a member's contact preferences.
    """

    class Meta:  # noqa: D101
        model = Member
        fields = ('newsletter', 'allow_user_messages',)


class MemberChangeNameForm(forms.ModelForm):
    """
    A form for editing a member's name.
    """

    class Meta:  # noqa: D101
        model = Member
        fields = ('name',)


class MemberChangeEmailForm(AllauthAddEmailForm):
    """
    Email-only subclass of account's SettingsForm.
    """

    timezone = None
    language = None


class ActivityMessageForm(forms.Form):
    """
    A form that allows a user to send a message to a project.
    """
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField()

    def send_mail(self, project_member_id, project):
        params = {
            'message': self.cleaned_data['message'],
            'project_member_id': project_member_id,
            'project': project,
        }

        plain = render_to_string('email/activity-message.txt', params)
        html = render_to_string('email/activity-message.html', params)

        send_mail('Open Humans: message from project member {}'
                  .format(project_member_id),
                  plain,
                  'no-reply@example.com',
                  [project.contact_email],
                  html_message=html)


class EmailUserForm(forms.Form):
    """
    A form that allows one user to email another user.
    """

    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField()

    def send_mail(self, sender, receiver):
        params = {
            'message': self.cleaned_data['message'],
            'sender': sender,
            'receiver': receiver,
        }

        plain = render_to_string('email/user-message.txt', params)
        html = render_to_string('email/user-message.html', params)

        send_mail('Open Humans: message from {} ({})'
                  .format(sender.member.name, sender.username),
                  plain,
                  sender.member.primary_email.email,
                  [receiver.member.primary_email.email],
                  html_message=html)


class ResetPasswordForm(AllauthResetPasswordForm):
    """
    Subclass django-allauths's ResetPasswordForm to capture the bit where we say
    what the return uri is.
    """

    def clean(self):
        cleaned_data = super().clean()
        if self._errors:
            return

        return cleaned_data

    def save(self, request, **kwargs):
        ret = super().save(request, **kwargs)

        self.cleaned_data['next'] = request.POST['next_t']
        member = Member.objects.get(user__email=ret)
        member.password_reset_redirect = self.cleaned_data['next']
        member.save()
        return ret
