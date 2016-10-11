import os

from boto.s3.connection import S3Connection

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet

from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import NeverCacheMixin
from common.permissions import HasValidToken

from data_import.utils import get_upload_path

from .api_authentication import ProjectTokenAuthentication
from .api_filter_backends import ProjectFilterBackend
from .api_permissions import HasValidProjectToken
from .forms import (DeleteDataFileForm, DirectUploadDataFileForm,
                    DirectUploadDataFileCompletionForm,
                    MessageProjectMembersForm, UploadDataFileForm)
from .models import (DataRequestProject, DataRequestProjectMember,
                     OAuth2DataRequestProject, ProjectDataFile)
from .serializers import ProjectDataSerializer, ProjectMemberDataSerializer

UserModel = get_user_model()


class ProjectAPIView(NeverCacheMixin):
    """
    The base class for all Project-related API views.
    """

    authentication_classes = (ProjectTokenAuthentication,)
    permission_classes = (HasValidProjectToken,)


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


class ProjectMemberExchangeView(NeverCacheMixin, RetrieveAPIView):
    """
    Return the project member information attached to the OAuth2 access token.
    """

    permission_classes = (HasValidToken,)
    serializer_class = ProjectMemberDataSerializer

    def get_object(self):
        """
        Get the project member related to the access_token.
        """
        project = OAuth2DataRequestProject.objects.get(
            application=self.request.auth.application)

        return DataRequestProjectMember.objects.get(
            member=self.request.user.member,
            project=project)


class ProjectMemberDataView(ProjectListView):
    """
    Return information about the project's members.
    """

    serializer_class = ProjectMemberDataSerializer

    def get_queryset(self):
        return DataRequestProjectMember.objects.filter_active()


class ProjectFormBaseView(ProjectAPIView, APIView):
    """
    A base view for uploads to Open Humans and S3 direct uploads.
    """

    def post(self, request):
        project = DataRequestProject.objects.get(
            master_access_token=self.request.auth.master_access_token)

        form = self.form_class(request.data, request.FILES)

        if not form.is_valid():
            raise serializers.ValidationError(form.errors)

        try:
            project_member = DataRequestProjectMember.objects.get(
                project=project,
                project_member_id=form.cleaned_data['project_member_id'])
        except DataRequestProjectMember.DoesNotExist:
            project_member = None

        if (not project_member or
                not project_member.joined or
                not project_member.authorized or
                project_member.revoked):
            raise serializers.ValidationError({
                'project_member_id': 'project_member_id is invalid'
            })

        self.project = project
        self.project_member = project_member
        self.form = form


class ProjectMessageView(ProjectAPIView, APIView):
    # pylint: disable=redefined-builtin, unused-argument
    def post(self, request, format=None):
        project = DataRequestProject.objects.get(
            master_access_token=self.request.auth.master_access_token)

        form = MessageProjectMembersForm(request.data)

        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        form.send_messages(project)

        return Response('success')


class ProjectFileDirectUploadView(ProjectFormBaseView):
    """
    Initiate a direct upload to S3 for a project by pre-signing and returning
    the URL.
    """

    form_class = DirectUploadDataFileForm

    def post(self, request):
        super(ProjectFileDirectUploadView, self).post(request)

        key = get_upload_path(self.project.id_label,
                              self.form.cleaned_data['filename'])

        data_file = ProjectDataFile(
            user=self.project_member.member.user,
            file=key,
            metadata=self.form.cleaned_data['metadata'],
            direct_sharing_project=self.project)

        data_file.save()

        s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                          settings.AWS_SECRET_ACCESS_KEY)

        url = s3.generate_url(
            expires_in=settings.INCOMPLETE_FILE_EXPIRATION_HOURS * 60 * 60,
            method='PUT',
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=key)

        return Response({
            'id': data_file.id,
            'url': url,
        }, status=status.HTTP_201_CREATED)


class ProjectFileDirectUploadCompletionView(ProjectFormBaseView):
    """
    Complete a direct upload for a project.
    """

    form_class = DirectUploadDataFileCompletionForm

    def post(self, request):
        super(ProjectFileDirectUploadCompletionView, self).post(request)

        data_file = ProjectDataFile.all_objects.get(
            pk=self.form.cleaned_data['file_id'])

        data_file.completed = True

        data_file.save()

        return Response({
            'status': 'ok',
            'size': data_file.size,
        }, status=status.HTTP_200_OK)


class ProjectFileUploadView(ProjectFormBaseView):
    """
    A form for uploading ProjectDataFiles to Open Humans.
    """

    form_class = UploadDataFileForm

    def post(self, request):
        super(ProjectFileUploadView, self).post(request)

        data_file = ProjectDataFile(
            user=self.project_member.member.user,
            file=self.form.cleaned_data['data_file'],
            metadata=self.form.cleaned_data['metadata'],
            direct_sharing_project=self.project,
            completed=True)

        data_file.save()

        return Response({'id': data_file.id}, status=status.HTTP_201_CREATED)


class ProjectFileDeleteView(ProjectFormBaseView):
    """
    A view for deleting a ProjectDataFile.
    """

    form_class = DeleteDataFileForm

    def post(self, request):
        super(ProjectFileDeleteView, self).post(request)

        file_id = self.form.cleaned_data['file_id']
        file_basename = self.form.cleaned_data['file_basename']
        all_files = self.form.cleaned_data['all_files']

        if not file_id and not file_basename and not all_files:
            raise serializers.ValidationError({
                'missing_field': ('one of file_id, file_basename, or '
                                  'all_files is required')
            })

        if len([field for field
                in [file_id, file_basename, all_files]
                if field]) > 1:
            raise serializers.ValidationError({
                'too_many': ('one of file_id, file_basename, or all_files is '
                             'required')
            })

        if file_id:
            data_files = [ProjectDataFile.objects.get(id=file_id)]

        if file_basename:
            data_files = ProjectDataFile.objects.filter(
                direct_sharing_project=self.project,
                user=self.project_member.member.user)

            data_files = [
                data_file for data_file in data_files
                if os.path.basename(data_file.file.name) == file_basename]

        if all_files:
            data_files = ProjectDataFile.objects.filter(
                direct_sharing_project=self.project,
                user=self.project_member.member.user)

        ids = [data_file.id for data_file in data_files]

        if isinstance(data_files, QuerySet):
            data_files.delete()
        else:
            for data_file in data_files:
                data_file.delete()

        return Response({'ids': ids}, status=status.HTTP_200_OK)
