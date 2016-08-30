from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^projects/oauth2/create/$',
        views.CreateOAuth2DataRequestProjectView.as_view(),
        name='create-oauth2'),

    url(r'^projects/on-site/create/$',
        views.CreateOnSiteDataRequestProjectView.as_view(),
        name='create-on-site'),

    url(r'^projects/on-site/join/(?P<slug>[a-z0-9-]+)/$',
        views.JoinOnSiteDataRequestProjectView.as_view(),
        name='join-on-site'),

    url(r'^projects/on-site/authorize/(?P<slug>[a-z0-9-]+)/$',
        views.AuthorizeOnSiteDataRequestProjectView.as_view(),
        name='authorize-on-site'),

    # Override /oauth2/authorize/ to specify our own context data
    url(r'^projects/oauth2/authorize/$',
        views.AuthorizeOAuth2ProjectView.as_view(),
        name='authorize-oauth2'),

    url(r'^projects/leave/(?P<pk>[0-9]+)/$',
        views.ProjectLeaveView.as_view(),
        name='leave-project'),

    url(r'^projects/oauth2/update/(?P<slug>[a-z0-9-]+)/$',
        views.UpdateOAuth2DataRequestProjectView.as_view(),
        name='update-oauth2'),

    url(r'^projects/on-site/update/(?P<slug>[a-z0-9-]+)/$',
        views.UpdateOnSiteDataRequestProjectView.as_view(),
        name='update-on-site'),

    url(r'^projects/oauth2/(?P<slug>[a-z0-9-]+)/$',
        views.OAuth2DataRequestProjectDetailView.as_view(),
        name='detail-oauth2'),

    url(r'^projects/on-site/(?P<slug>[a-z0-9-]+)/$',
        views.OnSiteDataRequestProjectDetailView.as_view(),
        name='detail-on-site'),

    url(r'^projects/manage/$',
        views.ManageDataRequestActivitiesView.as_view(),
        name='manage-projects'),

    url(r'^projects/message/(?P<slug>[a-z0-9-]+)/$',
        views.MessageProjectMembersView.as_view(),
        name='message-members'),

    # url(r'^projects/(?P<slug>[a-z0-9-]+)/$',
    #     views.ProjectHomeView.as_view(),
    #     name='home'),

    url(r'^in-development/$',
        views.InDevelopmentView.as_view(),
        name='in-development'),

    # Documentation
    url(r'^overview/$', views.OverviewView.as_view(), name='overview'),

    url(r'^on-site-features/$',
        TemplateView.as_view(
            template_name='direct-sharing/on-site-features.html'),
        name='on-site-features'),

    url(r'^on-site-setup/$',
        TemplateView.as_view(
            template_name='direct-sharing/on-site-setup.html'),
        name='on-site-setup'),

    url(r'^on-site-data-access/$',
        TemplateView.as_view(
            template_name='direct-sharing/on-site-data-access.html'),
        name='on-site-data-access'),

    url(r'^on-site-messages/$',
        TemplateView.as_view(
            template_name='direct-sharing/on-site-messages.html'),
        name='on-site-messages'),

    url(r'^on-site-data-upload/$',
        TemplateView.as_view(
            template_name='direct-sharing/on-site-data-upload.html'),
        name='on-site-data-upload'),

    url(r'^oauth2-features/$',
        TemplateView.as_view(template_name='direct-sharing/oauth2-features.html'),
        name='oauth2-features'),

    url(r'^oauth2-setup/$',
        TemplateView.as_view(template_name='direct-sharing/oauth2-setup.html'),
        name='oauth2-setup'),

    url(r'^oauth2-data-access/$',
        TemplateView.as_view(
            template_name='direct-sharing/oauth2-data-access.html'),
        name='oauth2-data-access'),

    url(r'^oauth2-messages/$',
        TemplateView.as_view(
            template_name='direct-sharing/oauth2-messages.html'),
        name='oauth2-messages'),

    url(r'^oauth2-data-upload/$',
        TemplateView.as_view(
            template_name='direct-sharing/oauth2-data-upload.html'),
        name='oauth2-data-upload'),
]
