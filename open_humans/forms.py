from account.forms import (SignupForm as AccountSignupForm,
                           SettingsForm as AccountSettingsForm)

from django.forms import BooleanField, CharField, ModelForm

from .models import Member


class SignupForm(AccountSignupForm):
    """
    A subclass of django-user-account's SignupForm with a `terms` field to add
    validation for the Terms of Use checkbox.
    """
    name = CharField(max_length=30)
    terms = BooleanField()

    class Meta:
        fields = '__all__'


class MyMemberProfileEditForm(ModelForm):
    """
    A form for editing a member's profile information.
    """
    class Meta:
        model = Member
        fields = ('profile_image', 'about_me',)


class MyMemberContactSettingsEditForm(ModelForm):
    """
    A form for editing a member's contact preferences.
    """
    class Meta:
        model = Member
        fields = ('newsletter', 'allow_user_messages',)


class MyMemberChangeNameForm(ModelForm):
    """
    A form for editing a member's name.
    """
    class Meta:
        model = Member
        fields = ('name',)


class MyMemberChangeEmailForm(AccountSettingsForm):
    """Email-only subclass of account's SettingsForm."""
    timezone = None
    language = None

    def __init__(self, *args, **kwargs):
        super(MyMemberChangeEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = "New email"
