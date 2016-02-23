from django import forms

from common.utils import get_source_labels_and_names

from .models import (OAuth2DataRequestActivity, OnSiteDataRequestActivity)

SOURCES = get_source_labels_and_names()


class DataRequestActivityForm(forms.ModelForm):
    """
    The base for all DataRequestActivity forms.
    """

    request_sources_access = forms.MultipleChoiceField(choices=SOURCES)

    def __init__(self, *args, **kwargs):
        super(DataRequestActivityForm, self).__init__(*args, **kwargs)

        override_fields = [
            'is_study',
            'active',
            'request_message_permission',
            'request_username_access'
        ]

        # XXX: feels like a hack; ideally we could just override the widget in
        # the Meta class but it doesn't work (you end up with an empty option)
        for field in override_fields:
            # set the widget to a RadioSelect
            self.fields[field].widget = forms.RadioSelect()

            # filter out the empty choice
            self.fields[field].choices = [
                choice for choice in self.fields[field].choices
                if choice[0] != ''
            ]

            # coerce the result to a boolean
            self.fields[field].coerce = lambda x: x == 'True'


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
