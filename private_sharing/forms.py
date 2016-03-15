from django import forms

from common.utils import get_source_labels_and_names

from .models import (OAuth2DataRequestProject, OnSiteDataRequestProject)

SOURCES = get_source_labels_and_names()


class DataRequestProjectForm(forms.ModelForm):
    """
    The base for all DataRequestProject forms.
    """

    request_sources_access = forms.MultipleChoiceField(choices=SOURCES)

    class Meta:
        fields = ('is_study', 'name', 'leader', 'organization',
                  'is_academic_or_nonprofit', 'contact_email', 'info_url',
                  'short_description', 'long_description', 'active',
                  'badge_image', 'request_sources_access',
                  'request_message_permission', 'request_username_access')

    def __init__(self, *args, **kwargs):
        super(DataRequestProjectForm, self).__init__(*args, **kwargs)

        self.fields['request_sources_access'].widget = (
            forms.CheckboxSelectMultiple())

        self.fields['request_sources_access'].required = False

        override_fields = [
            'is_study',
            'is_academic_or_nonprofit',
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


class OAuth2DataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:
        model = OAuth2DataRequestProject
        fields = DataRequestProjectForm.Meta.fields + ('enrollment_url',
                                                       'redirect_url')


class OnSiteDataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:
        model = OnSiteDataRequestProject
        fields = DataRequestProjectForm.Meta.fields + ('consent_text',
                                                       'post_sharing_url')
