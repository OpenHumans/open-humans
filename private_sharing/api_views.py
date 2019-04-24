import os

from boto.s3.connection import S3Connection
from botocore.exceptions import ClientError as BotoClientError

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet

from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import NeverCacheMixin

from data_import.models import DataFile
from data_import.serializers import DataFileSerializer
from data_import.utils import get_upload_path

from .api_authentication import CustomOAuth2Authentication, MasterTokenAuthentication
from .api_filter_backends import ProjectFilterBackend
from .api_permissions import HasValidProjectToken
from .forms import (
    DeleteDataFileForm,
    DirectUploadDataFileForm,
    DirectUploadDataFileCompletionForm,
    MessageProjectMembersForm,
    RemoveProjectMembersForm,
    UploadDataFileForm,
)
from .models import (
    DataRequestProject,
    DataRequestProjectMember,
    OAuth2DataRequestProject,
    ProjectDataFile,
)
from .serializers import ProjectDataSerializer, ProjectMemberDataSerializer

UserModel = get_user_model()


class ProjectAPIView(NeverCacheMixin):
    """
    The base class for all Project-related API views.
    """

    authentication_classes = (CustomOAuth2Authentication, MasterTokenAuthentication)
    permission_classes = (HasValidProjectToken,)

    def get_oauth2_member(self):
        """
        Return project member if auth by OAuth2 user access token, else None.
        """
        if self.request.auth.__class__ == OAuth2DataRequestProject:
            proj_member = DataRequestProjectMember.objects.get(
                member=self.request.user.member, project=self.request.auth
            )
            return proj_member
        return None


class ProjectDetailView(ProjectAPIView, RetrieveAPIView):
    """
    A detail view for the Project or models directly related to it.
    """

    def get_object(self):
        """
        Get the project related to the access_token.
        """
        return DataRequestProject.objects.get(pk=self.request.auth.pk)


class ProjectListView(ProjectAPIView, ListAPIView):
    """
    A list view for models directly related to the Project model.
    """

    filter_backends = (ProjectFilterBackend,)


class ProjectDataView(ProjectDetailView):
    """
    Return information about the project itself.
    """

    serializer_class = ProjectDataSerializer


class ProjectMemberExchangeView(NeverCacheMixin, ListAPIView):
    """
    Return the project member information attached to the OAuth2 access token.
    """

    authentication_classes = (CustomOAuth2Authentication, MasterTokenAuthentication)
    permission_classes = (HasValidProjectToken,)
    serializer_class = DataFileSerializer
    max_limit = 200
    default_limit = 100

    def get_object(self):
        """
        Get the project member related to the access_token.
        """
        # Determine which auth method was used; if OAuth2, self.request.auth.application
        # will exist; otherwise, self.request.auth is set to the project
        if hasattr(self.request.auth, "application"):
            project = OAuth2DataRequestProject.objects.get(
                application=self.request.auth.application
            )
            return DataRequestProjectMember.objects.get(
                member=self.request.user.member, project=project
            )
        project_member_id = self.request.GET.get("project_member_id", None)
        if project_member_id:
            project_member = DataRequestProjectMember.objects.filter(
                project_member_id=project_member_id, project=self.request.auth
            )
        if project_member.count() == 1:
            return project_member.get()
        # No or invalid project_member_id provided
        raise serializers.ValidationError(
            {"project_member_id": "project_member_id is invalid"}
        )

    def get_sources_shared(self, obj):
        """
        Get the other sources this project requests access to.
        """
        return [source.id_label for source in obj.granted_sources.all()]

    def get_username(self):
        """
        Only return the username if the user has shared it with the project.
        """
        if self.obj.username_shared:
            return self.obj.member.user.username

        return None

    def get_queryset(self):
        """
        Get the queryset of DataFiles that belong to a member in a project
        """
        self.obj = self.get_object()
        self.request.public_sources = list(
            self.obj.member.public_data_participant.publicdataaccess_set.filter(
                is_public=True
            ).values_list("data_source", flat=True)
        )
        all_files = DataFile.objects.filter(user=self.obj.member.user).exclude(
            parent_project_data_file__completed=False
        )

        if self.obj.all_sources_shared:
            files = all_files
        else:
            sources_shared = self.get_sources_shared(self.obj)
            sources_shared.append(self.obj.project.id_label)
            files = all_files.filter(source__in=sources_shared)
        return files.order_by("source", "id")

    def list(self, request, *args, **kwargs):
        """
        Add the additional fields to the api endpoint that our API is expected to have.
        """
        ret = super().list(request, *args, **kwargs)
        ret.data.update({"created": self.obj.created})
        ret.data.update({"project_member_id": self.obj.project_member_id})
        ret.data.update({"sources_shared": self.get_sources_shared(self.obj)})
        username = self.get_username()
        if username:
            ret.data.update({"username": username})
        # The list api returns 'results' but our api is expected to return 'data'
        # This renames the key
        data = ret.data.pop("results")
        ret.data.update({"data": data})
        return ret


class ProjectMemberDataView(ProjectListView):
    """
    Return information about the project's members.
    """

    authentication_classes = (MasterTokenAuthentication,)
    serializer_class = ProjectMemberDataSerializer
    max_limit = 20
    default_limit = 10

    def get_queryset(self):
        return DataRequestProjectMember.objects.filter_active()


class ProjectFormBaseView(ProjectAPIView, APIView):
    """
    A base view for uploads to Open Humans and S3 direct uploads.
    """

    def post(self, request):
        project_member = self.get_oauth2_member()
        project = DataRequestProject.objects.get(
            master_access_token=self.request.auth.master_access_token
        )

        # Just to be safe and maybe unneeded, but we don't want one user's
        # OAuth2 token to to allow a write to a different user's account.
        req_data = request.data.copy()
        if project_member:
            req_data["project_member_id"] = project_member.project_member_id

        try:
            form = self.form_class(req_data, request.FILES, project=project)
        except TypeError:
            form = self.form_class(req_data, request.FILES)

        if not form.is_valid():
            raise serializers.ValidationError(form.errors)

        if not project_member:
            try:
                project_member = DataRequestProjectMember.objects.get(
                    project=project,
                    project_member_id=form.cleaned_data["project_member_id"],
                )
            except DataRequestProjectMember.DoesNotExist:
                project_member = None

        if (
            not project_member
            or not project_member.joined
            or not project_member.authorized
            or project_member.revoked
        ):
            raise serializers.ValidationError(
                {"project_member_id": "project_member_id is invalid"}
            )

        self.project = project
        self.project_member = project_member
        self.form = form


class ProjMemberFormAPIMixin:
    """
    A mixin for API views using forms operating on project members.
    """

    def process_projmember_api_request(self):

        # We want to modify the request data before instantiating a form,
        # but the request object's data is immutable.
        request_data = self.request.data.copy()

        projmember = self.get_oauth2_member()
        project = DataRequestProject.objects.get(
            master_access_token=self.request.auth.master_access_token
        )

        # Prevent actions on other members using one member's OAuth2 token.
        # (These actions are possible with 'master token' authentication.)
        if projmember:
            request_data["all_members"] = False
            request_data["project_member_ids"] = [projmember.project_member_id]

        form = self.form_class(request_data, project=project)
        return form, project


class ProjectMessageView(ProjMemberFormAPIMixin, ProjectAPIView, APIView):
    """
    API view for sending messages to project members.
    """

    form_class = MessageProjectMembersForm

    def post(self, request, format=None):
        form, project = self.process_projmember_api_request()

        if not form.is_valid():
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        form.send_messages(project)
        return Response("success")


class ProjectRemoveMemberView(ProjMemberFormAPIMixin, ProjectAPIView, APIView):
    """
    API view for removing project members.
    """

    form_class = RemoveProjectMembersForm

    def post(self, request, format=None):
        form, project = self.process_projmember_api_request()

        if not form.is_valid():
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        form.remove_members(project)
        return Response("success")


class ProjectFileDirectUploadView(ProjectFormBaseView):
    """
    Initiate a direct upload to S3 for a project by pre-signing and returning
    the URL.
    """

    form_class = DirectUploadDataFileForm

    def post(self, request):
        super().post(request)

        key = get_upload_path(self.project.id_label, self.form.cleaned_data["filename"])

        datafile = ProjectDataFile(
            user=self.project_member.member.user,
            file=key,
            metadata=self.form.cleaned_data["metadata"],
            direct_sharing_project=self.project,
        )

        datafile.save()
        datafile.datatypes.set(self.form.cleaned_data["datatypes"])

        s3 = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

        url = s3.generate_url(
            expires_in=settings.INCOMPLETE_FILE_EXPIRATION_HOURS * 60 * 60,
            method="PUT",
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=key,
        )

        return Response({"id": datafile.id, "url": url}, status=status.HTTP_201_CREATED)


class ProjectFileDirectUploadCompletionView(ProjectFormBaseView):
    """
    Complete a direct upload for a project.
    """

    form_class = DirectUploadDataFileCompletionForm

    def post(self, request):
        super().post(request)
        # If upload failed, file_id would be empty.  Let's fail gracefully.
        file_id = self.form.cleaned_data.get("file_id", None)
        if not file_id:
            return Response(
                {"detail": "file does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        data_file = ProjectDataFile.all_objects.get(pk=file_id)

        data_file.completed = True
        data_file.save()

        try:
            return Response(
                {"status": "ok", "size": data_file.file.size}, status=status.HTTP_200_OK
            )
        except BotoClientError:
            data_file.completed = False
            data_file.save()
            return Response(
                {"detail": "file not present"}, status=status.HTTP_400_BAD_REQUEST
            )


class ProjectFileUploadView(ProjectFormBaseView):
    """
    A form for uploading ProjectDataFiles to Open Humans.
    """

    form_class = UploadDataFileForm

    def post(self, request):
        super().post(request)

        datafile = ProjectDataFile(
            user=self.project_member.member.user,
            file=self.form.cleaned_data["data_file"],
            metadata=self.form.cleaned_data["metadata"],
            direct_sharing_project=self.project,
            completed=True,
        )
        datafile.save()
        datafile.datatypes.set(self.form.cleaned_data["datatypes"])

        return Response({"id": datafile.id}, status=status.HTTP_201_CREATED)


class ProjectFileDeleteView(ProjectFormBaseView):
    """
    A view for deleting a ProjectDataFile.
    """

    form_class = DeleteDataFileForm

    def post(self, request):
        super(ProjectFileDeleteView, self).post(request)

        file_id = self.form.cleaned_data["file_id"]
        file_basename = self.form.cleaned_data["file_basename"]
        all_files = self.form.cleaned_data["all_files"]

        if not file_id and not file_basename and not all_files:
            raise serializers.ValidationError(
                {
                    "missing_field": (
                        "one of file_id, file_basename, or " "all_files is required"
                    )
                }
            )

        if len([field for field in [file_id, file_basename, all_files] if field]) > 1:
            raise serializers.ValidationError(
                {
                    "too_many": (
                        "one of file_id, file_basename, or all_files is " "required"
                    )
                }
            )

        if file_id:
            data_files = ProjectDataFile.objects.filter(id=file_id)
            if data_files.exists():
                data_files = [data_files.get()]
            else:
                data_files = []

        if file_basename:
            data_files = ProjectDataFile.objects.filter(
                direct_sharing_project=self.project,
                user=self.project_member.member.user,
            )

            data_files = [
                data_file
                for data_file in data_files
                if os.path.basename(data_file.file.name) == file_basename
            ]

        if all_files:
            data_files = ProjectDataFile.objects.filter(
                direct_sharing_project=self.project,
                user=self.project_member.member.user,
            )

        ids = [data_file.id for data_file in data_files]

        if isinstance(data_files, QuerySet):
            data_files.delete()
        else:
            for data_file in data_files:
                data_file.delete()

        return Response({"ids": ids}, status=status.HTTP_200_OK)
