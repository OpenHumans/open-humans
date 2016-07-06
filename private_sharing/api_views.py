import os

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import NeverCacheMixin
from common.permissions import HasValidToken

from .api_authentication import ProjectTokenAuthentication
from .api_filter_backends import ProjectFilterBackend
from .api_permissions import HasValidProjectToken
from .forms import (DeleteDataFileForm, MessageProjectMembersForm,
                    UploadDataFileForm)
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
        return DataRequestProjectMember.objects.filter(
            revoked=False,
            authorized=True)


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


class ProjectFileUploadView(ProjectAPIView, APIView):
    # pylint: disable=redefined-builtin, unused-argument
    def post(self, request, format=None):
        project = DataRequestProject.objects.get(
            master_access_token=self.request.auth.master_access_token)

        form = UploadDataFileForm(request.data, request.FILES)

        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

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
            return Response(
                {
                    'errors': {
                        'project_member_id': 'project_member_id is invalid'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST)

        data_file = ProjectDataFile(
            user=project_member.member.user,
            file=form.cleaned_data['data_file'],
            metadata=form.cleaned_data['metadata'],
            direct_sharing_project=project)

        data_file.save()

        return Response({'id': data_file.id}, status=status.HTTP_201_CREATED)


class ProjectFileDeleteView(ProjectAPIView, APIView):
    # pylint: disable=redefined-builtin, unused-argument
    def post(self, request, format=None):
        project = DataRequestProject.objects.get(
            master_access_token=self.request.auth.master_access_token)

        form = DeleteDataFileForm(request.data)

        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

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
            return Response(
                {
                    'errors': {
                        'project_member_id': 'project_member_id is invalid'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST)

        file_id = form.cleaned_data['file_id']
        file_basename = form.cleaned_data['file_basename']
        all_files = form.cleaned_data['all_files']

        if not file_id and not file_basename and not all_files:
            return Response(
                {
                    'errors': {
                        'missing_field': ('one of file_id, file_basename, or '
                                          'all_files is required')
                    }
                },
                status=status.HTTP_400_BAD_REQUEST)

        if len([field for field
                in [file_id, file_basename, all_files]
                if field]) > 1:
            return Response(
                {
                    'errors': {
                        'too_many': ('one of file_id, file_basename, or '
                                     'all_files is required')
                    }
                },
                status=status.HTTP_400_BAD_REQUEST)

        if file_id:
            data_files = ProjectDataFile.objects.get(id=file_id)

        if file_basename:
            data_files = ProjectDataFile.objects.filter(
                direct_sharing_project=project,
                user=project_member.member.user)

            data_files = [
                data_file for data_file in data_files
                if os.path.basename(data_file.file.name) == file_basename]

        if all_files:
            data_files = ProjectDataFile.objects.filter(
                direct_sharing_project=project,
                user=project_member.member.user)

        ids = [data_file.id for data_file in data_files]

        data_files.delete()

        return Response({'ids': ids}, status=status.HTTP_200_OK)
