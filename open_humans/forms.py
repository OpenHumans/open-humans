from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from allauth.account import app_settings as account_settings
from allauth.account.forms import (
    ChangePasswordForm as AllauthChangePasswordForm,
    LoginForm as AllauthLoginForm,
    ResetPasswordForm as AllauthResetPasswordForm,
    SignupForm as AllauthSignupForm,
    SetPasswordForm as AllauthSetPasswordForm,
)
from allauth.account.models import EmailAddress
from allauth.account.utils import filter_users_by_email
from allauth.socialaccount.forms import SignupForm as AllauthSocialSignupForm

from .models import Member

User = get_user_model()


def _clean_password(child_class, self_instance, password_field_name):
    """
    A custom password validator that enforces a minimum length.
    """
    min_len = settings.ACCOUNT_PASSWORD_MIN_LENGTH
    # Also use parent method if django-user-accounts ever implements it.
    parent_clean_password = getattr(
        super(child_class, self_instance), "clean_" + password_field_name, None
    )
    if parent_clean_password:
        parent_clean_password()
    if len(self_instance.cleaned_data[password_field_name]) < min_len:
        raise forms.ValidationError(
            "Password should be at least " + "%d characters long." % min_len
        )
    return self_instance.cleaned_data[password_field_name]


class MemberLoginForm(AllauthLoginForm):
    """
    A subclass of django-allauth's form that checks user is a Member.
    """

    authentication_fail_message = (
        "Your password didn't match the " + "username or email you provided."
    )

    def clean(self):
        """Check that the user is a Member."""
        cleaned_data = super().clean()
        if self._errors:
            return
        if self.user:

            try:
                Member.objects.get(user=self.user)
            except Member.DoesNotExist:
                raise forms.ValidationError("This account doesn't have a Member role.")

        return cleaned_data


class MemberSignupForm(AllauthSignupForm):
    """
    A subclass of django-allauth's SignupForm with additions.

    A `terms` field is added for the Terms of Use checkbox, and a `name` field
    is added to store a Member's username.
    """

    name = forms.CharField(max_length=30)
    terms = forms.BooleanField()
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:  # noqa: D101
        fields = "__all__"


class MemberProfileEditForm(forms.ModelForm):
    """
    A form for editing a member's profile information.
    """

    class Meta:  # noqa: D101
        model = Member
        fields = ("profile_image", "about_me")


class MemberContactSettingsEditForm(forms.ModelForm):
    """
    A form for editing a member's contact preferences.
    """

    class Meta:  # noqa: D101
        model = Member
        fields = ("newsletter", "allow_user_messages")


class MemberChangeNameForm(forms.ModelForm):
    """
    A form for editing a member's name.
    """

    class Meta:  # noqa: D101
        model = Member
        fields = ("name",)


class MemberChangeUsernameForm(forms.ModelForm):
    """
    A form for editing a member's username.
    """

    def clean_username(self):
        username = self.cleaned_data["username"]
        for validator in account_settings.USERNAME_VALIDATORS:
            validator(username)
        return username

    class Meta:  # noqa: D101
        model = User
        fields = ("username",)
        help_texts = {"username": "Letters, number, or underscore only."}


class ActivityMessageForm(forms.Form):
    """
    A form that allows a user to send a message to a project.
    """

    message = forms.CharField(widget=forms.Textarea)
    if not settings.DEBUG:
        captcha = ReCaptchaField(widget=ReCaptchaV3)

    def send_mail(self, project_member_id, project):
        params = {
            "message": self.cleaned_data["message"],
            "project_member_id": project_member_id,
            "project": project,
        }

        plain = render_to_string("email/activity-message.txt", params)
        html = render_to_string("email/activity-message.html", params)

        send_mail(
            "Open Humans: message from project member {}".format(project_member_id),
            plain,
            "no-reply@example.com",
            [project.contact_email],
            html_message=html,
        )


class EmailUserForm(forms.Form):
    """
    A form that allows one user to email another user.
    """

    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def send_mail(self, sender, receiver):
        params = {
            "message": self.cleaned_data["message"],
            "sender": sender,
            "receiver": receiver,
        }

        plain = render_to_string("email/user-message.txt", params)
        html = render_to_string("email/user-message.html", params)

        send_mail(
            "Open Humans: message from {} ({})".format(
                sender.member.name, sender.username
            ),
            plain,
            sender.member.primary_email.email,
            [receiver.member.primary_email.email],
            html_message=html,
        )


class ResetPasswordForm(AllauthResetPasswordForm):
    """
    Subclass django-allauths's ResetPasswordForm to capture the bit where we
    say what the return uri is.
    """

    def save(self, request, **kwargs):
        next_url = request.session.pop("next_url", reverse(settings.LOGIN_REDIRECT_URL))

        ret = super().save(request, **kwargs)
        # Use the lookup method allauth uses to get relevant members.
        users = filter_users_by_email(ret)
        for user in users:
            member = Member.objects.get(user=user)
            member.password_reset_redirect = next_url
            member.save()

        return ret


class SocialSignupForm(AllauthSocialSignupForm):
    """
    Add in extra form bits that we need that allauth's social account signup
    form does not provide by default.
    """

    name = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "Write your name here"}),
    )
    newsletter = forms.BooleanField(required=False)
    allow_contact = forms.BooleanField(required=False)
    terms = forms.BooleanField()

    def save(self, request):
        """
        Make sure to also populate the member table
        """
        user = super().save(request)
        member = Member(user=user)
        member.name = self.cleaned_data["name"]
        member.newsletter = self.cleaned_data["newsletter"]
        member.allow_user_messages = self.cleaned_data["allow_contact"]
        member.save()
        # And, populate the email field in the user table
        account_emailaddress = EmailAddress.objects.get(
            email=self.cleaned_data["email"]
        )
        user.email = account_emailaddress.email
        user.save()
        # We are trusting emails provided by Facebook and Google
        account_emailaddress.verified = True
        account_emailaddress.save()

        return user
