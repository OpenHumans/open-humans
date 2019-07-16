from django.urls import path, re_path

from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views

app_name = "api"

urlpatterns = [
    # DataFile endpoints
    path(
        "public/datafiles/",
        api_views.PublicDataFileListAPIView.as_view(),
        name="datafiles",
    ),
    re_path(
        "public/datafile/(?P<pk>[0-9]+)/",
        api_views.PublicDataFileAPIView.as_view(),
        name="datafile",
    ),
    # DataType endpoints
    path(
        "public/datatypes/",
        api_views.PublicDataTypeListAPIView.as_view(),
        name="datatypes",
    ),
    re_path(
        "public/datatype/(?P<pk>[0-9]+)/datafiles/",
        api_views.PublicDataTypeDataFilesAPIView.as_view(),
        name="datatype-datafiles",
    ),
    re_path(
        "public/datatype/(?P<pk>[0-9]+)/",
        api_views.PublicDataTypeAPIView.as_view(),
        name="datatype",
    ),
    # Member endpoints
    path(
        "public/members/", api_views.PublicMemberListAPIView.as_view(), name="members"
    ),
    re_path(
        "public/member/(?P<user__username>[A-Za-z_0-9]+)/datafiles/",
        api_views.PublicMemberDataFilesAPIView.as_view(),
        name="member-datafiles",
    ),
    re_path(
        "public/member/(?P<user__username>[A-Za-z_0-9]+)/projects/",
        api_views.PublicMemberProjectsAPIView.as_view(),
        name="member-projects",
    ),
    re_path(
        "public/member/(?P<user__username>[A-Za-z_0-9]+)/",
        api_views.PublicMemberAPIView.as_view(),
        name="member",
    ),
    # Project endpoints
    re_path(
        "public/project/(?P<pk>[0-9]+)/datafiles/",
        api_views.PublicProjectDataFilesAPIView.as_view(),
        name="project-datafiles",
    ),
    re_path(
        "public/project/(?P<pk>[0-9]+)/members",
        api_views.PublicProjectMembersAPIView.as_view(),
        name="project-members",
    ),
    re_path(
        "public/project/(?P<pk>[0-9]+)/",
        api_views.PublicProjectAPIView.as_view(),
        name="project",
    ),
    path(
        "public/projects/",
        api_views.PublicProjectListAPIView.as_view(),
        name="projects",
    ),
    # Legacy endpoints
    path("public-data/", api_views.PublicDataListAPIView.as_view(), name="public-data"),
    path(
        "public-data/sources-by-member/",
        api_views.PublicDataSourcesByUserAPIView.as_view(),
    ),
    path(
        "public-data/members-by-source/",
        api_views.PublicDataUsersBySourceAPIView.as_view(),
        name="members-by-source",
    ),
]


urlpatterns = format_suffix_patterns(urlpatterns)
