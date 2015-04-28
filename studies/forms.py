from account.forms import (LoginUsernameForm as AccountLoginUsernameForm,
                           SignupForm as AccountSignupForm)
from django import forms

from open_humans.forms import _clean_password

from .models import Researcher


class ResearcherLoginForm(AccountLoginUsernameForm):
    """
    A subclass of django-user-account's form that checks user is a Researcher.
    """
    authentication_fail_message = ("Your password didn't match the " +
                                   "username or email you provided.")

    def clean(self):
        """Check that the user is a Researcher."""
        cleaned_data = super(ResearcherLoginForm, self).clean()

        if self.user:
            try:
                Researcher.objects.get(user=self.user)
            except Researcher.DoesNotExist:
                raise forms.ValidationError(
                    "This account doesn't have a Researcher role.")
        return cleaned_data


class ResearcherSignupForm(AccountSignupForm):
    """
    A subclass of django-user-account's SignupForm with additions.

    A `terms` field is added for the Terms of Use checkbox, a `name` field
    is added to store a Researcher's name, and additional validation is
    added for passwords to impose a minimum length.
    """
    name = forms.CharField(max_length=30)
    terms = forms.BooleanField()

    class Meta:
        fields = '__all__'

    def clean_password(self):
        return _clean_password(AccountSignupForm, self, 'password')
