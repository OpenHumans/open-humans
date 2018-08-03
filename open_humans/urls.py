from account.views import ChangePasswordView, PasswordResetTokenView

from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from social.apps.django_app.views import auth as social_auth_login

import data_import.urls
import private_sharing.api_urls
import private_sharing.urls
import public_data.urls

from . import account_views, api_urls, views, member_views
from .forms import ChangePasswordForm, PasswordResetTokenForm

handler500 = 'open_humans.views.server_error'

app_name = 'open_humans'

urlpatterns = [
    path('admin/', include((admin.site.urls[0], admin.site.urls[1]), namespace=admin.site.urls[2])),

    # Include the various APIs here
    path('api/', include(api_urls)),
    path('api/direct-sharing/', include(private_sharing.api_urls)),

    # Override social auth login to require Open Humans login
    re_path(r'^auth/login/(?P<backend>[^/]+)/$',
            login_required(social_auth_login),
            name='begin'),

    # Authentication with python-social-auth reqs top-level 'social' namespace.
    path('auth/', include('social.apps.django_app.urls', namespace='social')),

    # from data_import, but alternate name as it is not specific to import
    path('data-management/', include(data_import.urls,
                                     namespace='data-management')),

    # Override /oauth2/authorize/ to specify our own context data
    path('oauth2/authorize/',
         views.AuthorizationView.as_view(),
         name='authorize'),

    # The URLs used for the OAuth2 dance (e.g. requesting an access token)
    path('oauth2/', include('oauth2_provider.urls',
                            namespace='oauth2_provider')),

    # URLs used for private data sharing activities
    path('direct-sharing/', include(private_sharing.urls,
                                    namespace='direct-sharing')),

    # URLs used for the Open Humans: Public Data Sharing study.
    path('public-data/', include(public_data.urls, namespace='public-data')),

    # Simple pages
    path('', views.HomeView.as_view(), name='home'),
    path('statistics/',
         views.StatisticView.as_view(template_name='pages/statistics.html'),
         name='statistics'),
    path('about/', TemplateView.as_view(template_name='pages/about.html'),
         name='about'),
    path('add-data/', views.AddDataPageView.as_view(), name='add-data'),
    path('explore-share/',
         views.ExploreSharePageView.as_view(), name='explore-share'),
    path('create/', views.CreatePageView.as_view(), name='create'),
    path('grants/',
         TemplateView.as_view(template_name='pages/project-grants.html'),
         name='project-grants'),
    path('jobs/', TemplateView.as_view(template_name='pages/jobs.html'),
         name='jobs'),
    path('community-guidelines/',
         TemplateView.as_view(template_name='pages/community_guidelines.html'),
         name='community_guidelines'),
    path('contact-us/',
         TemplateView.as_view(template_name='pages/contact_us.html'),
         name='contact_us'),
    path('copyright/',
         TemplateView.as_view(template_name='pages/copyright-policy.html'),
         name='copyright-policy'),
    path('data-use/',
         TemplateView.as_view(template_name='pages/data-use.html'),
         name='data-use-policy'),
    path('faq/',
         RedirectView.as_view(url=reverse_lazy('contact_us'), permanent=True),
         name='faq'),
    path('news/',
         TemplateView.as_view(template_name='pages/news.html'),
         name='news'),
    path('terms/',
         TemplateView.as_view(template_name='pages/terms.html'),
         name='terms-of-use'),
    path('public-data-api/',
         views.PublicDataDocumentationView.as_view(),
         name='public-data-api'),
    path('grant-projects/',
         views.GrantProjectView.as_view(),
         name='grant-projects'),

    # Override to use custom form and view with added fields and methods.
    path('account/signup/', account_views.MemberSignupView.as_view(),
         name='account_signup'),

    # Override to check that the user has a Member role.
    path('account/login/', account_views.MemberLoginView.as_view(),
         name='account_login'),

    # More overrides - custom forms to enforce password length minimum.
    path('account/password/',
         ChangePasswordView.as_view(form_class=ChangePasswordForm),
         name='account_password'),

    re_path(r'^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            PasswordResetTokenView.as_view(form_class=PasswordResetTokenForm),
            name='account_password_reset_token'),

    # django-account's built-in delete uses a configurable expunge timer,
    # let's just do it immediately and save the complexity
    path('account/delete/',
         account_views.UserDeleteView.as_view(),
         name='account_delete'),

    # Custom view for prompting login when performing OAuth2 authorization
    path('account/login/oauth2/', views.OAuth2LoginView.as_view(),
         name='account-login-oauth2'),

    # This has to be after the overriden account/ URLs, not before
    path('account/', include('account.urls')),

    # Member views of their own accounts.
    path('member/me/', member_views.MemberDashboardView.as_view(),
         name='my-member-dashboard'),

    path('member/me/edit/',
         member_views.MemberProfileEditView.as_view(),
         name='my-member-profile-edit'),

    path('member/me/joined/',
         member_views.MemberJoinedView.as_view(),
         name='my-member-joined'),

    path('member/me/data/',
         member_views.MemberDataView.as_view(),
         name='my-member-data'),

    re_path(r'^member/me/research-data/delete/(?P<source>[a-z0-9-_]+)/$',
            views.SourceDataFilesDeleteView.as_view(),
            name='delete-source-data-files'),

    path('member/me/account-settings/',
         member_views.MemberSettingsEditView.as_view(),
         name='my-member-settings'),

    path('member/me/connections/',
         member_views.MemberConnectionsView.as_view(),
         name='my-member-connections'),

    re_path(r'^member/me/connections/delete/(?P<connection>[a-z-_]+)/$',
            member_views.MemberConnectionDeleteView.as_view(),
            name='my-member-connections-delete'),

    path('member/me/change-email/',
         account_views.MemberChangeEmailView.as_view(),
         name='my-member-change-email'),

    path('member/me/change-name/',
         member_views.MemberChangeNameView.as_view(),
         name='my-member-change-name'),

    path('member/me/send-confirmation-email/',
         member_views.MemberSendConfirmationEmailView.as_view(),
         name='my-member-send-confirmation-email'),

    # Public/shared views of member accounts
    path('members/',
         member_views.MemberListView.as_view(),
         name='member-list'),

    re_path(r'^members/page/(?P<page>\d+)/$',
            member_views.MemberListView.as_view(),
            name='member-list-paginated'),

    re_path(r'^member/(?P<slug>[A-Za-z_0-9]+)/$',
            member_views.MemberDetailView.as_view(),
            name='member-detail'),

    re_path(r'^member/(?P<slug>[A-Za-z_0-9]+)/email/$',
            member_views.MemberEmailView.as_view(),
            name='member-email'),

    re_path(r'^activity/(?P<source>[A-Za-z0-9_-]+)/$',
            views.ActivityManagementView.as_view(),
            name='activity-management'),

    re_path(r'^activity/(?P<source>[A-Za-z0-9_-]+)/send-message/$',
            views.ActivityMessageFormView.as_view(),
            name='activity-messaging'),

    path('201805-notice-of-terms-update/',
         TemplateView.as_view(template_name='pages/201805-notice-of-terms-update.html'),
         name='201805-notice-of-terms-update'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG or settings.TESTING:
    urlpatterns += [
        path('raise-exception/', views.ExceptionView.as_view()),
    ]

# Must be the very last URL so that user URLs don't conflict with other URLs
urlpatterns += [
    re_path(r'^(?P<slug>[A-Za-z_0-9]+)/$',
            member_views.MemberDetailView.as_view(),
            name='member-detail-direct'),
]
