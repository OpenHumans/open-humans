import json
import re

import arrow

from django import forms
from django.core.mail.message import EmailMultiAlternatives
from django.urls import reverse
from django.template import engines
from django.template.loader import render_to_string

from common.utils import full_url

from .models import (DataRequestProject,
                     DataRequestProjectMember,
                     OAuth2DataRequestProject,
                     OnSiteDataRequestProject,
                     active_help_text,
                     post_sharing_url_help_text)

class DataRequestProjectForm(forms.Form):
    """
    The base for all DataRequestProject forms
    """
    BOOL_CHOICES = [(True, 'Yes'), (False, 'No')]
    name = forms.CharField(label='Project name',
                           max_length=100,
                           required=True)
    is_study = forms.ChoiceField(choices=[(True, 'Study'), (False, 'Activity')],
                                 label='Is this project a study or an activity?',
                                 help_text=('A "study" is doing human subjects '
                                            'research and must have '
                                            'Institutional Review Board '
                                            'approval or equivalent ethics '
                                            'board oversight. Activities can '
                                            'be anything else, e.g. data '
                                            'visualizations.'),
                                 required=True,
                                 widget=forms.RadioSelect())
    leader = forms.CharField(label='Leader(s) or principal investigator(s)',
                             max_length=100,
                             required=True)
    organization = forms.CharField(label='Organization or institution',
                                   max_length=100,
                                   required=False)
    is_academic_or_nonprofit = forms.ChoiceField(
        choices=BOOL_CHOICES,
        required=True,
        help_text=('Is this institution or organization an academic '
                   'institution or non-profit organization?'),
        widget=forms.RadioSelect())
    add_data = forms.BooleanField(
        required=False,
        help_text=('If your project collects data, choose "Add data" here. If '
                   'you choose "Add data", you will need to provide a '
                   '"Returned data description" below.'),
        label='Add data')
    explore_share = forms.BooleanField(
        required=False,
        help_text=('If your project performs analysis on data, choose '
                   '"Explore & share".'),
        label='Explore & share')
    contact_email = forms.EmailField(label='Contact email for your project',
                                     required=True)
    info_url = forms.URLField(
        required=False,
        label='URL for general information about your project')
    short_description = forms.CharField(
        max_length=140,
        required=True,
        label='A short description (140 characters max)')
    long_description = forms.CharField(
        max_length=1000,
        required=True,
        label='A long description (1000 characters max)',
        widget=forms.Textarea)
    returned_data_description = forms.CharField(
        max_length=140,
        required=False,
        label=('Description of data you plan to upload to member '
               ' accounts (140 characters max)'),
        help_text=("Leave this blank if your project doesn't plan to add or "
                   'return new data for your members.  If your project is set '
                   'to be displayed under "Add data", then you must provide '
                   'this information.'))
    active = forms.ChoiceField(
        choices=BOOL_CHOICES,
        required=True,
        help_text=active_help_text,
        widget=forms.RadioSelect())
    badge_image = forms.ImageField(
        max_length=1024,
        required=False,
        help_text=("A badge that will be displayed on the user's profile once "
                   "they've connected your project."))
    request_username_access = forms.ChoiceField(
        choices=BOOL_CHOICES,
        required=True,
        help_text=("Access to the member's username. This implicitly enables "
                   'access to anything the user is publicly sharing on Open '
                   'Humans. Note that this is potentially sensitive and/or '
                   'identifying.'),
        label='Are you requesting Open Humans usernames?',
        widget=forms.RadioSelect())
    erasure_supported = forms.BooleanField(
        required=False,
        label='Member data erasure supported',
        widget=forms.CheckboxInput())
    deauth_email_notification = forms.BooleanField(
        required=False,
        help_text="Receive emails when a member deauthorizes your project",
        label="Deauthorize email notifications",
        widget=forms.CheckboxInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        source_projects = (DataRequestProject.objects
                           .filter(approved=True)
                           .exclude(returned_data_description=''))
        sources = [(project.id_label, project.name)
                   for project in source_projects]

        self.fields['request_sources_access'] = forms.MultipleChoiceField(
            choices=sources,
            help_text=('List of sources this project is requesting access to '
                       'on Open Humans.'))

        self.fields['request_sources_access'].widget = (
            forms.CheckboxSelectMultiple())

        self.fields['request_sources_access'].required = False

    def clean(self):
        """
        Logic to for conditional required elements in our form.
        """
        cleaned_data = super().clean()

        add_data = cleaned_data.get('add_data', False)
        explore_share = cleaned_data.get('explore_share', False)
        returned_data_description = cleaned_data.get(
            'returned_data_description', None)

        if not (add_data or explore_share):
            self.add_error('add_data',
                           forms.ValidationError('Pick at least one option '
                                                 'from "Add data" and "Explore '
                                                 'and share"'))
        if add_data:
            if not returned_data_description:
                self.add_error('returned_data_description',
                               forms.ValidationError('Please provide a '
                                                     'description of the data '
                                                     'you plan to upload to '
                                                     'member accounts.'))
        return cleaned_data


class OAuth2DataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """
    enrollment_url = forms.URLField(
        help_text=("The URL we direct members to if they're interested in "
                   'sharing data with your project.'),
        required=True,
        label='Enrollment URL')
    redirect_url = forms.URLField(
        max_length=256,
        help_text="""the return url for our "authorization code" oauth2 grant
        process. you can <a target="_blank" href="{0}">read more about oauth2
        "authorization code" transactions here</a>.""".format(
            '/direct-sharing/oauth2-setup/#setup-oauth2-authorization'),
        label='redirect url',
        required=True)

    deauth_webhook = forms.URLField(
        max_length=256,
        help_text="""the url to send a post to when a member
        requests data erasure.  this request will be in the form
        of json,
        { 'project_member_id': '12345678', 'erasure_requested': true}""",
        label='deauthorization webhook url',
        required=True)


class OnSiteDataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """
    consent_text = forms.CharField(
        required=True,
        help_text=('The "informed consent" text that describes your project '
                   'to Open Humans members.'),
        widget=forms.Textarea)
    post_sharing_url = forms.URLField(
        label='Post-sharing URL',
        required=False,
        help_text=post_sharing_url_help_text)


class BaseProjectMembersForm(forms.Form):
    """
    Base form for taking actions with a list of project members IDs.
    """
    project_member_ids = forms.CharField(
        label='Project member IDs',
        help_text='A comma-separated list of project member IDs.',
        # TODO: we could validate one of (all_members, project_member_ids) on
        # the client-side.
        required=False,
        widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(BaseProjectMembersForm, self).__init__(*args, **kwargs)

    def clean_project_member_ids(self):
        raw_ids = self.data.get('project_member_ids', '')

        # the HTML form is a comma-delimited string; the API is a list
        if not isinstance(raw_ids, str):
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
        project_members = (DataRequestProjectMember.objects
                           .filter_active()
                           .filter(project_member_id__in=project_member_ids)
                           .filter(project=self.project))

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


class MessageProjectMembersForm(BaseProjectMembersForm):
    """
    A form for validating messages and emailing the members of a project.
    """

    all_members = forms.BooleanField(
        label='Message all project members?',
        required=False)

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
            project_members = project.project_members.filter_active().all()
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
            headers = {'Reply-To': project.contact_email}

            mail = EmailMultiAlternatives(
                subject,
                plain,
                '{} <{}>'.format(project.name, 'support@openhumans.org'),
                [project_member.member.primary_email.email],
                headers=headers)
            mail.send()


class RemoveProjectMembersForm(BaseProjectMembersForm):

    def clean(self):
        if not self.data.get('project_member_ids'):
            raise forms.ValidationError(
                'You must provide a list of project member IDs.')

    def remove_members(self, project):
        project_members = self.cleaned_data['project_member_ids']
        invalid_members = []
        for project_member in project_members:
            if project_member.project != project:
                invalid_members.append(project_member.project_member_id)
        if invalid_members:
            msg = 'Project member IDs not in this project: {}'.format(
                invalid_members)
            raise ValueError(msg)

        # Only run member removal if no invalid members.
        for project_member in project_members:
            project_member.leave_project(done_by='project-coordinator')


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

        if not isinstance(metadata['description'], str):
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
