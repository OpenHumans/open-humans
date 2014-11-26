from account.forms import SignupForm as AccountSignupForm

from django.forms import BooleanField, ModelForm

from .models import Member


class SignupForm(AccountSignupForm):
    """
    A subclass of django-user-account's SignupForm with a `terms` field to add
    validation for the Terms of Use checkbox.
    """
    terms = BooleanField()

    class Meta:
        fields = '__all__'


class MyMemberProfileEditForm(ModelForm):

    class Meta:
        model = Member
        fields = ('profile_image', 'about_me',)


class MyMemberContactSettingsEditForm(ModelForm):

    class Meta:
        model = Member
        fields = ('newsletter', 'allow_user_messages',)
