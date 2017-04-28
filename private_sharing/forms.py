import json
import re

import arrow

from django import forms
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import engines
from django.template.loader import render_to_string

from common.utils import full_url

from .models import (DataRequestProjectMember, OAuth2DataRequestProject,
                     OnSiteDataRequestProject)
from .utilities import get_source_labels_and_names_including_dynamic


class DataRequestProjectForm(forms.ModelForm):
    """
    The base for all DataRequestProject forms.
    """

    class Meta:  # noqa: D101
        fields = ('is_study', 'name', 'leader', 'organization',
                  'is_academic_or_nonprofit', 'contact_email', 'info_url',
                  'short_description', 'long_description',
                  'returned_data_description', 'active', 'badge_image',
                  'request_sources_access', 'request_message_permission',
                  'request_username_access')

    def __init__(self, *args, **kwargs):
        super(DataRequestProjectForm, self).__init__(*args, **kwargs)

        sources = [s for s in get_source_labels_and_names_including_dynamic()
                   if s[0] != self.instance.id_label]

        self.fields['request_sources_access'] = forms.MultipleChoiceField(
            choices=sources)

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

    class Meta:  # noqa: D101
        model = OAuth2DataRequestProject
        fields = DataRequestProjectForm.Meta.fields + ('enrollment_url',
                                                       'redirect_url')


class OnSiteDataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:  # noqa: D101
        model = OnSiteDataRequestProject
        fields = DataRequestProjectForm.Meta.fields + ('consent_text',
                                                       'post_sharing_url')


class MessageProjectMembersForm(forms.Form):
    """
    A form for validating messages and emailing the members of a project.
    """

    all_members = forms.BooleanField(
        label='Message all project members?',
        required=False)

    project_member_ids = forms.CharField(
        label='Project member IDs',
        help_text='A comma-separated list of project member IDs.',
        # TODO: we could validate one of (all_members, project_member_ids) on
        # the client-side.
        required=False,
        widget=forms.Textarea)

    subject = forms.CharField(
        label='Message subject',
        help_text='''A prefix is added to create the outgoing email subject.
        e.g. "[Open Humans Project Message] Your subject here"''',
        required=False)

    message = forms.CharField(
        label='Message text',
        help_text="""The text of the message to send to each project member
        specified above. You may use <code>{{ PROJECT_MEMBER_ID }}</code> in
        your message text and it will be replaced with the project member ID in
        the message sent to the member.""",
        required=True,
        widget=forms.Textarea)

    def clean_project_member_ids(self):
        raw_ids = self.data.get('project_member_ids', '')

        # the HTML form is a comma-delimited string; the API is a list
        if not isinstance(raw_ids, basestring):
            raw_ids = ','.join(raw_ids)

        project_member_ids = re.split(r'[ ,\r\n]+', raw_ids)

        # remove empty IDs
        project_member_ids = [project_member_id for project_member_id
                              in project_member_ids if project_member_id]

        # check for malformed IDs
        if any([True for project_member_id in project_member_ids
                if len(project_member_id) != 8 and
                len(project_member_id) != 16]):
            raise forms.ValidationError(
                'Project member IDs are always 8 digits long.')

        # look up each ID in the database
        project_members = DataRequestProjectMember.objects.filter(
            project_member_id__in=project_member_ids,
            message_permission=True)

        # if some of the project members weren't found then they were invalid
        if len(project_member_ids) != len(project_members):
            def in_project_members(project_member_id):
                for project_member in project_members:
                    if project_member.project_member_id == project_member_id:
                        return True

            raise forms.ValidationError(
                'Invalid project member ID(s): {0}'.format(', '.join([
                    project_member_id
                    for project_member_id in project_member_ids
                    if not in_project_members(project_member_id)])))

        # return the actual objects
        return project_members

    def clean(self):
        cleaned_data = super(MessageProjectMembersForm, self).clean()

        all_members = cleaned_data.get('all_members')
        # get this from the raw data because invalid IDs are cleaned out
        project_member_ids = self.data.get('project_member_ids')

        if not all_members and not project_member_ids:
            raise forms.ValidationError(
                'You must specify either all members or provide a list of '
                'IDs.')

        if all_members and project_member_ids:
            raise forms.ValidationError(
                'You must specify either all members or provide a list of IDs '
                'but not both.')

    def send_messages(self, project):
        template = engines['django'].from_string(self.cleaned_data['message'])

        subject = '[Open Humans Project Message] '
        if 'subject' in self.cleaned_data and self.cleaned_data['subject']:
            subject += self.cleaned_data['subject']
        else:
            subject += 'From "{}"'.format(project.name)

        if self.cleaned_data['all_members']:
            project_members = project.project_members.filter(
                message_permission=True)
        else:
            project_members = self.cleaned_data['project_member_ids']

        for project_member in project_members:
            context = {
                'message': template.render({
                    'PROJECT_MEMBER_ID': project_member.project_member_id
                }),
                'project': project.name,
                'username': project_member.member.user.username,
                'activity_management_url': full_url(reverse(
                    'activity-management',
                    kwargs={'source': project.slug})),
                'project_message_form': full_url(reverse(
                    'activity-messaging',
                    kwargs={'source': project.slug})),
            }

            plain = render_to_string('email/project-message.txt', context)

            send_mail(subject,
                      plain,
                      '{} <{}>'.format(project.name, project.contact_email),
                      [project_member.member.primary_email.email])


class UploadDataFileBaseForm(forms.Form):
    """
    The base form for S3 direct uploads and regular uploads.
    """

    project_member_id = forms.CharField(
        label='Project member ID',
        required=True)

    metadata = forms.CharField(
        label='Metadata',
        required=True)

    def clean_metadata(self):
        try:
            metadata = json.loads(self.cleaned_data['metadata'])
        except ValueError:
            raise forms.ValidationError(
                'could not parse the uploaded metadata')

        if 'description' not in metadata:
            raise forms.ValidationError(
                '"description" is a required field of the metadata')

        if not isinstance(metadata['description'], basestring):
            raise forms.ValidationError(
                '"description" must be a string')

        if 'tags' not in metadata:
            raise forms.ValidationError(
                '"tags" is a required field of the metadata')

        if not isinstance(metadata['tags'], list):
            raise forms.ValidationError(
                '"tags" must be an array of strings')

        def validate_date(date):
            try:
                arrow.get(date)
            except arrow.parser.ParserError:
                raise forms.ValidationError('Dates must be in ISO 8601 format')

        if 'creation_date' in metadata:
            validate_date(metadata['creation_date'])

        if 'start_date' in metadata:
            validate_date(metadata['start_date'])

        if 'end_date' in metadata:
            validate_date(metadata['end_date'])

        if 'md5' in metadata:
            if not re.match(r'[a-z0-9]{32}', metadata['md5'],
                            flags=re.IGNORECASE):
                raise forms.ValidationError('Invalid MD5 specified')

        return metadata


class UploadDataFileForm(UploadDataFileBaseForm):
    """
    A form for validating uploaded files from a project.
    """

    data_file = forms.FileField(
        label='Data file',
        required=True)


class DirectUploadDataFileForm(UploadDataFileBaseForm):
    """
    A form for validating the direct upload of files for a project.
    """

    filename = forms.CharField(
        label='File name',
        required=True)


class DirectUploadDataFileCompletionForm(forms.Form):
    """
    A form for validating the completion of a direct upload.
    """

    file_id = forms.IntegerField(
        required=False,
        label='File ID')

    project_member_id = forms.CharField(
        label='Project member ID',
        required=True)


class DeleteDataFileForm(forms.Form):
    """
    A form for validating the deletion of files for a project.
    """

    project_member_id = forms.CharField(
        label='Project member ID',
        required=True)

    file_id = forms.IntegerField(
        required=False,
        label='File ID')

    file_basename = forms.CharField(
        required=False,
        label='File basename')

    all_files = forms.BooleanField(
        required=False,
        label='All files')
