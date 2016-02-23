from django import forms

from common.utils import get_source_labels_and_names

from .models import OAuth2DataRequestActivity, OnSiteDataRequestActivity

SOURCES = get_source_labels_and_names()


class DataRequestActivityForm(forms.ModelForm):
    """
    The base for all DataRequestActivity forms.
    """

    request_sources_access = forms.MultipleChoiceField(choices=SOURCES)


class OAuth2DataRequestActivityForm(DataRequestActivityForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:
        model = OAuth2DataRequestActivity
        fields = ('is_study', 'name', 'leader', 'organization',
                  'contact_email', 'info_url', 'short_description',
                  'long_description', 'active', 'request_sources_access',
                  'request_message_permission', 'request_username_access',
                  'enrollment_text', 'redirect_url')


class OnSiteDataRequestActivityForm(forms.ModelForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:
        model = OnSiteDataRequestActivity
        fields = ('is_study', 'name', 'leader', 'organization',
                  'contact_email', 'info_url', 'short_description',
                  'long_description', 'active', 'request_sources_access',
                  'request_message_permission', 'request_username_access',
                  'consent_text', 'post_sharing_url')
