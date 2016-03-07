from account.forms import (
    ChangePasswordForm as AccountChangePasswordForm,
    LoginUsernameForm as AccountLoginUsernameForm,
    PasswordResetTokenForm as AccountPasswordResetTokenForm,
    SettingsForm as AccountSettingsForm,
    SignupForm as AccountSignupForm,
)

from captcha.fields import ReCaptchaField

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Member


def _clean_password(child_class, self_instance, password_field_name):
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


class MemberLoginForm(AccountLoginUsernameForm):
    """
    A subclass of django-user-account's form that checks user is a Member.
    """
    authentication_fail_message = ("Your password didn't match the " +
                                   'username or email you provided.')

    def clean(self):
        """Check that the user is a Member."""
        cleaned_data = super(MemberLoginForm, self).clean()

        if self.user:
            try:
                Member.objects.get(user=self.user)
            except Member.DoesNotExist:
                raise forms.ValidationError(
                    "This account doesn't have a Researcher role.")

        return cleaned_data


class MemberSignupForm(AccountSignupForm):
    """
    A subclass of django-user-account's SignupForm with additions.

    A `terms` field is added for the Terms of Use checkbox, a `name` field
    is added to store a Member's username, and additional validation is
    added for passwords to impose a minimum length.
    """
    name = forms.CharField(max_length=30)
    terms = forms.BooleanField()

    class Meta:
        fields = '__all__'

    def clean_password(self):
        return _clean_password(AccountSignupForm, self, 'password')


class ChangePasswordForm(AccountChangePasswordForm):
    """
    A subclass of account's ChangePasswordForm that checks password length.
    """
    def clean_password_new(self):
        return _clean_password(ChangePasswordForm, self, 'password_new')


class PasswordResetTokenForm(AccountPasswordResetTokenForm):
    """
    A subclass of account's PasswordResetTokenForm that checks password length.
    """
    def clean_password(self):
        return _clean_password(PasswordResetTokenForm, self, 'password')


class MemberProfileEditForm(forms.ModelForm):
    """
    A form for editing a member's profile information.
    """
    class Meta:
        model = Member
        fields = ('profile_image', 'about_me',)


class MemberContactSettingsEditForm(forms.ModelForm):
    """
    A form for editing a member's contact preferences.
    """
    class Meta:
        model = Member
        fields = ('newsletter', 'allow_user_messages',)


class MemberChangeNameForm(forms.ModelForm):
    """
    A form for editing a member's name.
    """
    class Meta:
        model = Member
        fields = ('name',)


class MemberChangeEmailForm(AccountSettingsForm):
    """
    Email-only subclass of account's SettingsForm.
    """
    timezone = None
    language = None

    def __init__(self, *args, **kwargs):
        super(MemberChangeEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'New email'


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
