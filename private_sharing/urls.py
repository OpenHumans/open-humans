from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views

app_name = 'direct-sharing'

urlpatterns = [
    path('projects/oauth2/create/',
         views.CreateOAuth2DataRequestProjectView.as_view(),
         name='create-oauth2'),

    path('projects/on-site/create/',
         views.CreateOnSiteDataRequestProjectView.as_view(),
         name='create-on-site'),

    re_path(r'^projects/on-site/join/(?P<slug>[a-z0-9_-]+)/$',
            views.JoinOnSiteDataRequestProjectView.as_view(),
            name='join-on-site'),

    re_path(r'^projects/on-site/authorize/(?P<slug>[a-z0-9_-]+)/$',
            views.AuthorizeOnSiteDataRequestProjectView.as_view(),
            name='authorize-on-site'),

    # Override /oauth2/authorize/ to specify our own context data
    path('projects/oauth2/authorize/',
         views.AuthorizeOAuth2ProjectView.as_view(),
         name='authorize-oauth2'),

    path('authorize-inactive/',
         TemplateView.as_view(
             template_name='private_sharing/authorize-inactive.html'),
         name='authorize-inactive'),

    re_path(r'^projects/leave/(?P<pk>[0-9]+)/$',
            views.ProjectLeaveView.as_view(),
            name='leave-project'),

    re_path(r'^projects/oauth2/update/(?P<slug>[a-z0-9_-]+)/$',
            views.UpdateOAuth2DataRequestProjectView.as_view(),
            name='update-oauth2'),

    re_path(r'^projects/on-site/update/(?P<slug>[a-z0-9_-]+)/$',
            views.UpdateOnSiteDataRequestProjectView.as_view(),
            name='update-on-site'),

    re_path(r'^projects/oauth2/(?P<slug>[a-z0-9_-]+)/$',
            views.OAuth2DataRequestProjectDetailView.as_view(),
            name='detail-oauth2'),

    re_path(r'^projects/on-site/(?P<slug>[a-z0-9_-]+)/$',
            views.OnSiteDataRequestProjectDetailView.as_view(),
            name='detail-on-site'),

    path('projects/manage/',
          views.ManageDataRequestActivitiesView.as_view(),
          name='manage-projects'),

    re_path(r'^projects/message/(?P<slug>[a-z0-9_-]+)/$',
            views.MessageProjectMembersView.as_view(),
            name='message-members'),

    re_path(r'^projects/remove-members/(?P<slug>[a-z0-9_-]+)/$',
            views.RemoveProjectMembersView.as_view(),
            name='remove-members'),

    re_path(r'^projects/withdrawn-members/(?P<slug>[a-z0-9_-]+)/$',
            views.DataRequestProjectWithdrawnView.as_view(),
            name='withdrawn-members'),

    re_path(r'^in-development/$',
            views.InDevelopmentView.as_view(),
            name='in-development'),

    # Documentation
    path('overview/', views.OverviewView.as_view(), name='overview'),

    path('approval/',
         TemplateView.as_view(
             template_name='direct-sharing/approval.html'),
         name='project-approval'),

    path('on-site-features/',
         TemplateView.as_view(
             template_name='direct-sharing/on-site-features.html'),
         name='on-site-features'),

    path('on-site-setup/',
         TemplateView.as_view(
             template_name='direct-sharing/on-site-setup.html'),
         name='on-site-setup'),

    path('on-site-data-access/',
         TemplateView.as_view(
             template_name='direct-sharing/on-site-data-access.html'),
         name='on-site-data-access'),

    path('on-site-messages/',
         TemplateView.as_view(
             template_name='direct-sharing/on-site-messages.html'),
         name='on-site-messages'),

    path('on-site-member-removal/',
         TemplateView.as_view(
             template_name='direct-sharing/on-site-member-removal.html'),
         name='on-site-member-removal'),

    path('on-site-data-upload/',
         TemplateView.as_view(
             template_name='direct-sharing/on-site-data-upload.html'),
         name='on-site-data-upload'),

    path('oauth2-features/',
         TemplateView.as_view(
             template_name='direct-sharing/oauth2-features.html'),
         name='oauth2-features'),

    path('oauth2-setup/',
         TemplateView.as_view(template_name='direct-sharing/oauth2-setup.html'),
         name='oauth2-setup'),

    path('oauth2-data-access/',
         TemplateView.as_view(
             template_name='direct-sharing/oauth2-data-access.html'),
         name='oauth2-data-access'),

    path('oauth2-messages/',
         TemplateView.as_view(
             template_name='direct-sharing/oauth2-messages.html'),
         name='oauth2-messages'),

    path('oauth2-member-removal/',
         TemplateView.as_view(
             template_name='direct-sharing/oauth2-member-removal.html'),
         name='oauth2-member-removal'),

    path('oauth2-data-upload/',
         TemplateView.as_view(
             template_name='direct-sharing/oauth2-data-upload.html'),
         name='oauth2-data-upload'),
]
