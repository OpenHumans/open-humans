from account.forms import SignupForm as AccountSignupForm

from django.forms import BooleanField, ModelForm

from .models import Profile


class SignupForm(AccountSignupForm):
    """
    A subclass of django-user-account's SignupForm with a `terms` field to add
    validation for the Terms of Use checkbox.
    """
    terms = BooleanField()

    class Meta:
        fields = '__all__'


class ProfileEditForm(ModelForm):

    class Meta:
        model = Profile
        fields = ('profile_image', 'about_me',)


class SettingsEditForm(ModelForm):

    class Meta:
        model = Profile
        fields = ('newsletter', 'allow_user_messages',)
