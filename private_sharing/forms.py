import json
import re

from django import forms

import arrow
from kombu.exceptions import KombuError

from common import tasks
from data_import.models import DataType

from .models import (
    DataRequestProject,
    DataRequestProjectMember,
    OAuth2DataRequestProject,
    OnSiteDataRequestProject,
)


def project_contain_no_url(value): 
  """
  check that value does not contain a link to a website
  """
  regex = "https?"
  if re.findall(regex, value, re.I): 
    raise forms.ValidationError("Error validating form") 


def project_contain_no_banned_words(value):
    """
    check that value doesn't include common spam words
    """
    words = [
        'buy', 'sell', 'betting', '88', '66', 'paypal', 
        'casino', 'escort', 'kasino', 'gambling', 'renting', 
        'SEO', 'www', 'hire' ,'.com', 'win', 'limousine',
        'leading', 'poker', 'provider', 'brand', 'product',
        'estate', 'solutions', 'business', 'call', 'whatsapp', 'gmail'
        ]
    for w in words:
        if re.findall(w, value, re.I):
            raise forms.ValidationError("Error validating form") 


class DataRequestProjectForm(forms.ModelForm):
    """
    The base for all DataRequestProject forms
    """

    long_description = forms.CharField(
        validators=[project_contain_no_url, project_contain_no_banned_words],
        widget=forms.Textarea)

    short_description = forms.CharField(
        validators=[project_contain_no_banned_words, project_contain_no_url]
    )

    name = forms.CharField(
        validators=[project_contain_no_banned_words, project_contain_no_url]
    )

    class Meta:  # noqa: D101

        fields = (
            "is_study",
            "name",
            "leader",
            "organization",
            "is_academic_or_nonprofit",
            "add_data",
            "explore_share",
            "contact_email",
            "info_url",
            "short_description",
            "long_description",
            "returned_data_description",
            "active",
            "badge_image",
            "request_username_access",
            "erasure_supported",
            "deauth_email_notification",
            "requested_sources",
            "jogl_page",
        )

    def __init__(self, *args, **kwargs):
        """
        Add custom handling for requested_sources and override some widgets.
        """
        super().__init__(*args, **kwargs)

        source_projects = DataRequestProject.objects.filter(approved=True).exclude(
            returned_data_description=""
        )
        self.fields["requested_sources"].choices = [
            (p.id, p.name) for p in source_projects
        ]
        self.fields["requested_sources"].widget = forms.CheckboxSelectMultiple()
        self.fields["requested_sources"].required = False

        override_fields = [
            "is_study",
            "is_academic_or_nonprofit",
            "active",
            "request_username_access",
        ]

        # XXX: feels like a hack; ideally we could just override the widget in
        # the Meta class but it doesn't work (you end up with an empty option)
        for field in override_fields:
            # set the widget to a RadioSelect
            self.fields[field].widget = forms.RadioSelect()

            # filter out the empty choice
            self.fields[field].choices = [
                choice for choice in self.fields[field].choices if choice[0] != ""
            ]

            # coerce the result to a boolean
            self.fields[field].coerce = lambda x: x == "True"

    def clean(self):
        """
        Logic to for conditional required elements in our form.
        """
        cleaned_data = super().clean()

        add_data = cleaned_data.get("add_data", False)
        explore_share = cleaned_data.get("explore_share", False)
        returned_data_description = cleaned_data.get("returned_data_description", None)

        if not (add_data or explore_share):
            self.add_error(
                "add_data",
                forms.ValidationError(
                    "Pick at least one option "
                    'from "Add data" and "Explore '
                    'and share"'
                ),
            )
        if add_data:
            if not returned_data_description:
                self.add_error(
                    "returned_data_description",
                    forms.ValidationError(
                        "Please provide a "
                        "description of the data "
                        "you plan to upload to "
                        "member accounts."
                    ),
                )
        return cleaned_data


class OAuth2DataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:  # noqa: D101
        model = OAuth2DataRequestProject
        fields = DataRequestProjectForm.Meta.fields + (
            "enrollment_url",
            "terms_url",
            "redirect_url",
            "webhook_secret",
            "deauth_webhook",
        )


class OnSiteDataRequestProjectForm(DataRequestProjectForm):
    """
    A form for editing a study data requirement.
    """

    class Meta:  # noqa: D101
        model = OnSiteDataRequestProject
        fields = DataRequestProjectForm.Meta.fields + (
            "consent_text",
            "post_sharing_url",
        )


class BaseProjectMembersForm(forms.Form):
    """
    Base form for taking actions with a list of project members IDs.
    """

    project_member_ids = forms.CharField(
        label="Project member IDs",
        help_text="A comma-separated list of project member IDs.",
        # TODO: we could validate one of (all_members, project_member_ids) on
        # the client-side.
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super(BaseProjectMembersForm, self).__init__(*args, **kwargs)

    def clean_project_member_ids(self):
        raw_ids = self.data.get("project_member_ids", "")

        # the HTML form is a comma-delimited string; the API is a list
        if not isinstance(raw_ids, str):
            raw_ids = ",".join(raw_ids)

        project_member_ids = re.split(r"[ ,\r\n]+", raw_ids)

        # remove empty IDs
        project_member_ids = [
            project_member_id
            for project_member_id in project_member_ids
            if project_member_id
        ]

        # check for malformed IDs
        if any(
            [
                True
                for project_member_id in project_member_ids
                if len(project_member_id) != 8 and len(project_member_id) != 16
            ]
        ):
            raise forms.ValidationError("Project member IDs are always 8 digits long.")

        # look up each ID in the database
        project_members = (
            DataRequestProjectMember.objects.filter_active()
            .filter(project_member_id__in=project_member_ids)
            .filter(project=self.project)
        )

        # if some of the project members weren't found then they were invalid
        if len(project_member_ids) != len(project_members):

            def in_project_members(project_member_id):
                for project_member in project_members:
                    if project_member.project_member_id == project_member_id:
                        return True

            raise forms.ValidationError(
                "Invalid project member ID(s): {0}".format(
                    ", ".join(
                        [
                            project_member_id
                            for project_member_id in project_member_ids
                            if not in_project_members(project_member_id)
                        ]
                    )
                )
            )

        # return the actual objects
        return project_members


class MessageProjectMembersForm(BaseProjectMembersForm):
    """
    A form for validating messages and emailing the members of a project.
    """

    all_members = forms.BooleanField(
        label="Message all project members?", required=False
    )

    subject = forms.CharField(
        label="Message subject",
        help_text='''A prefix is added to create the outgoing email subject.
        e.g. "[Open Humans Project Message] Your subject here"''',
        required=False,
    )

    message = forms.CharField(
        label="Message text",
        help_text="""The text of the message to send to each project member
        specified above. You may use <code>{{ PROJECT_MEMBER_ID }}</code> in
        your message text and it will be replaced with the project member ID in
        the message sent to the member.""",
        required=True,
        widget=forms.Textarea,
    )

    def clean(self):
        cleaned_data = super(MessageProjectMembersForm, self).clean()

        all_members = cleaned_data.get("all_members")
        # get this from the raw data because invalid IDs are cleaned out
        project_member_ids = self.data.get("project_member_ids")

        if not all_members and not project_member_ids:
            raise forms.ValidationError(
                "You must specify either all members or provide a list of " "IDs."
            )

        if all_members and project_member_ids:
            raise forms.ValidationError(
                "You must specify either all members or provide a list of IDs "
                "but not both."
            )

    def send_messages(self, project):
        message = self.cleaned_data["message"]

        subject = "[Open Humans Project Message] "
        if "subject" in self.cleaned_data and self.cleaned_data["subject"]:
            subject += self.cleaned_data["subject"]
        else:
            subject += 'From "{}"'.format(project.name)

        # celery wants data to be serialized as json (or pickle, but we're using
        # json).  Thus, we need to pass objects that are directly serializable
        # as such; the db objects will be referenced within the Celery task
        project_members = list(
            self.cleaned_data["project_member_ids"].values_list(
                "project_member_id", flat=True
            )
        )
        all_members = self.cleaned_data.get("all_members", False)

        # 201905 workaround for this: https://github.com/celery/kombu/issues/1019
        attempts = 0
        while True:
            try:
                tasks.send_emails.delay(
                    project.id,
                    project_members,
                    subject,
                    message,
                    all_members=all_members,
                )
                break
            except KombuError as error:
                attempts += 1
                if attempts < 5:
                    continue
                raise error


class RemoveProjectMembersForm(BaseProjectMembersForm):
    def clean(self):
        if not self.data.get("project_member_ids"):
            raise forms.ValidationError(
                "You must provide a list of project member IDs."
            )

    def remove_members(self, project):
        project_members = self.cleaned_data["project_member_ids"]
        invalid_members = []
        for project_member in project_members:
            if project_member.project != project:
                invalid_members.append(project_member.project_member_id)
        if invalid_members:
            msg = "Project member IDs not in this project: {}".format(invalid_members)
            raise ValueError(msg)

        # Only run member removal if no invalid members.
        for project_member in project_members:
            project_member.leave_project(done_by="project-coordinator")


class UploadDataFileBaseForm(forms.Form):
    """
    The base form for S3 direct uploads and regular uploads.
    """

    project_member_id = forms.CharField(label="Project member ID", required=True)

    metadata = forms.CharField(label="Metadata", required=True)

    # TODO: When updated to require datatypes - should set required to true.
    datatypes = forms.CharField(label="Data type", required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super().__init__(*args, **kwargs)

    def _get_datatypes(self, dt_list, method):
        """
        Get DataType objects from IDs or names, report if unmatched and unregistered.
        """
        assert method in ["id", "name"]
        datatypes, unregistered, unmatched = [], [], []
        registered_datatypes = self.project.registered_datatypes.all()
        for item in dt_list:
            try:
                if method == "id":
                    dt = DataType.objects.get(id=int(item))
                elif method == "name":
                    dt = DataType.objects.get(name__iexact=item)
                if self.project.any_datatypes or dt in registered_datatypes:
                    datatypes.append(dt)
                else:
                    unregistered.append(item)
            except DataType.DoesNotExist:
                unmatched.append(item)
        return datatypes, unregistered, unmatched

    def clean_datatypes(self):
        """
        Cleans and returns DataType objects specified by JSON list of IDs or names.
        """
        # TODO: When updated to require datatypes - no longer handle missing field.
        if not self.cleaned_data["datatypes"]:
            if self.project.auto_add_datatypes:
                return self.project.registered_datatypes.all()
            else:
                return []

        # Load as JSON-fomatted list
        try:
            dt_set = set(json.loads(self.cleaned_data["datatypes"]))
        except ValueError:
            raise forms.ValidationError(
                "Could not parse the uploaded datatypes from: '{}'".format(
                    self.cleaned_data["datatypes"]
                )
            )

        # Try loading as IDs first, then names.
        try:
            datatypes, notreg, notmatch = self._get_datatypes(dt_set, method="id")
        except ValueError:
            datatypes, notreg, notmatch = self._get_datatypes(dt_set, method="name")

        # Error fon unmatched datatypes.
        if notmatch:
            raise forms.ValidationError(
                "The following datatypes don't match items in our database: {}".format(
                    notmatch
                )
            )

        # Error for unregistered datatypes.
        if notreg:
            raise forms.ValidationError(
                "The following datatypes aren't registered for this project: {}".format(
                    notreg
                )
            )

        return datatypes

    def clean_metadata(self):
        try:
            metadata = json.loads(self.cleaned_data["metadata"])
        except ValueError:
            raise forms.ValidationError("could not parse the uploaded metadata")

        if "description" not in metadata:
            raise forms.ValidationError(
                '"description" is a required field of the metadata'
            )

        if not isinstance(metadata["description"], str):
            raise forms.ValidationError('"description" must be a string')

        if "tags" not in metadata:
            raise forms.ValidationError('"tags" is a required field of the metadata')

        if not isinstance(metadata["tags"], list):
            raise forms.ValidationError('"tags" must be an array of strings')

        def validate_date(date):
            try:
                arrow.get(date)
            except arrow.parser.ParserError:
                raise forms.ValidationError("Dates must be in ISO 8601 format")

        if "creation_date" in metadata:
            validate_date(metadata["creation_date"])

        if "start_date" in metadata:
            validate_date(metadata["start_date"])

        if "end_date" in metadata:
            validate_date(metadata["end_date"])

        if "md5" in metadata:
            if not re.match(r"[a-z0-9]{32}", metadata["md5"], flags=re.IGNORECASE):
                raise forms.ValidationError("Invalid MD5 specified")

        return metadata


class UploadDataFileForm(UploadDataFileBaseForm):
    """
    A form for validating uploaded files from a project.
    """

    data_file = forms.FileField(label="Data file", required=True)


class DirectUploadDataFileForm(UploadDataFileBaseForm):
    """
    A form for validating the direct upload of files for a project.
    """

    filename = forms.CharField(label="File name", required=True)


class DirectUploadDataFileCompletionForm(forms.Form):
    """
    A form for validating the completion of a direct upload.
    """

    file_id = forms.IntegerField(required=False, label="File ID")

    project_member_id = forms.CharField(label="Project member ID", required=True)


class DeleteDataFileForm(forms.Form):
    """
    A form for validating the deletion of files for a project.
    """

    project_member_id = forms.CharField(label="Project member ID", required=True)

    file_id = forms.IntegerField(required=False, label="File ID")

    file_basename = forms.CharField(required=False, label="File basename")

    all_files = forms.BooleanField(required=False, label="All files")


class SelectDatatypesForm(forms.ModelForm):
    """
    Select registered datatypes for a project.
    """

    class Meta:  # noqa: D101
        model = DataRequestProject
        fields = ["registered_datatypes"]
        widgets = {"registered_datatypes": forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["registered_datatypes"].required = False
