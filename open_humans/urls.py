from account.views import ChangePasswordView, PasswordResetTokenView

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from .forms import ChangePasswordForm, PasswordResetTokenForm
from .views import (
    ActivitiesView, AuthorizationView, DataRetrievalTaskDeleteView,
    EmailUserView, ExceptionView, HomeView, MemberDetailView, MemberListView,
    MemberLoginView, MemberSignupView, MyMemberChangeEmailView,
    MyMemberChangeNameView, MyMemberConnectionDeleteView,
    MyMemberConnectionsView, MyMemberDashboardView, MyMemberDatasetsView,
    MyMemberProfileEditView, MyMemberSettingsEditView,
    MyMemberSendConfirmationEmailView, MyMemberStudyGrantDeleteView,
    OAuth2LoginView, PGPInterstitialView, StatisticsView, UserDeleteView,
    WelcomeView)

from . import api_urls

import activities.urls
import data_import.urls
import public_data.urls
import studies.urls_api
import studies.urls_study

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    # Include the various APIs here
    url(r'^api/', include(studies.urls_api)),
    url(r'^api/', include(api_urls)),

    # Authentication with python-social-auth reqs top-level 'social' namespace.
    url(r'^auth/', include('social.apps.django_app.urls', namespace='social')),

    # URLs used for activity-related interactions.
    url(r'^activity/', include(activities.urls, namespace='activities')),

    # URLs used for study-related interactions.
    url(r'^study/', include(studies.urls_study, namespace='studies')),

    # data_import urls for data import management (for studies and activities)
    url(r'^data-import/', include(data_import.urls, namespace='data-import')),
    # alternate name: app contains other things not specific to import.
    url(r'^data-management/', include(data_import.urls,
                                      namespace='data-management')),

    # Override /oauth2/authorize/ to specify our own context data
    url(r'^oauth2/authorize/$', AuthorizationView.as_view(), name='authorize'),

    # The URLs used for the OAuth2 dance (e.g. requesting an access token)
    url(r'^oauth2/', include('oauth2_provider.urls',
                             namespace='oauth2_provider')),

    # URLs used for the Open Humans: Public Data Sharing study.
    url(r'^public-data/', include(public_data.urls, namespace='public-data')),

    # Simple pages
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),
    url(r'^research/$', TemplateView.as_view(
        template_name='pages/research.html'), name='research'),
    url(r'^community-guidelines/$',
        TemplateView.as_view(template_name='pages/community_guidelines.html'),
        name='community_guidelines'),
    url(r'^contact-us/$',
        TemplateView.as_view(template_name='pages/contact_us.html'),
        name='contact_us'),
    url(r'^copyright/$',
        TemplateView.as_view(template_name='pages/copyright-policy.html'),
        name='copyright-policy'),
    url(r'^data-use/$',
        TemplateView.as_view(template_name='pages/data-use.html'),
        name='data-use-policy'),
    url(r'^faq/$',
        TemplateView.as_view(template_name='pages/faq.html'),
        name='faq'),
    url(r'^news/$',
        TemplateView.as_view(template_name='pages/news.html'),
        name='news'),
    url(r'^terms/$',
        TemplateView.as_view(template_name='pages/terms.html'),
        name='terms-of-use'),
    url(r'^activities/$', ActivitiesView.as_view(), name='activities'),
    url(r'^statistics/$', StatisticsView.as_view(), name='statistics'),
    url(r'^pgp-quick-note/$', PGPInterstitialView.as_view(),
        name='pgp-interstitial'),

    # Override to use custom form and view with added fields and methods.
    url(r'^account/signup/$', MemberSignupView.as_view(),
        name='account_signup'),
    # Override to check that the user has a Member role.
    url(r'^account/login/$', MemberLoginView.as_view(),
        name='account_login'),
    # More overrides - custom forms to enforce password length minimum.
    url(r'^account/password/$',
        ChangePasswordView.as_view(form_class=ChangePasswordForm),
        name='account_password'),
    url(r'^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetTokenView.as_view(form_class=PasswordResetTokenForm),
        name='account_password_reset_token'),
    # django-account's built-in delete uses a configurable expunge timer,
    # let's just do it immediately and save the complexity
    url(r'^account/delete/$', UserDeleteView.as_view(), name='account_delete'),
    # Custom view for prompting login when performing OAuth2 authorization
    url(r'^account/login/oauth2', OAuth2LoginView.as_view(),
        name='account_login_oauth2'),
    # This has to be after the overriden account/ URLs, not before
    url(r'^account/', include('account.urls')),

    # Member views of their own accounts.
    url(r'^member/me/$', MyMemberDashboardView.as_view(),
        name='my-member-dashboard'),

    url(r'^member/me/edit/$',
        MyMemberProfileEditView.as_view(),
        name='my-member-profile-edit'),

    url(r'^member/me/research-data/$',
        MyMemberDatasetsView.as_view(),
        name='my-member-research-data'),

    url(r'^member/me/research-data/delete/(?P<pk>[0-9]+)/$',
        DataRetrievalTaskDeleteView.as_view(),
        name='delete-data-retrieval-task'),

    url(r'^member/me/account-settings/$',
        MyMemberSettingsEditView.as_view(),
        name='my-member-settings'),

    url(r'^member/me/connections/$',
        MyMemberConnectionsView.as_view(),
        name='my-member-connections'),

    url(r'^member/me/connections/delete/(?P<connection>[a-z-_]+)/$',
        MyMemberConnectionDeleteView.as_view(),
        name='my-member-connections-delete'),

    url(r'^member/me/study-grants/delete/(?P<study_grant>[a-z0-9-_]+)/$',
        MyMemberStudyGrantDeleteView.as_view(),
        name='my-member-study-grants-delete'),

    url(r'^member/me/change-email/$',
        MyMemberChangeEmailView.as_view(),
        name='my-member-change-email'),

    url(r'^member/me/change-name/$',
        MyMemberChangeNameView.as_view(),
        name='my-member-change-name'),

    url(r'^member/me/send-confirmation-email/$',
        MyMemberSendConfirmationEmailView.as_view(),
        name='my-member-send-confirmation-email'),

    # Welcome pages to guide new members.
    url(r'^welcome/$', WelcomeView.as_view(), name='welcome'),

    url(r'^welcome/enrollment/$',
        WelcomeView.as_view(template_name='member/welcome-enrollment.html'),
        name='welcome-enrollment'),

    url(r'^welcome/connecting/$',
        WelcomeView.as_view(template_name='member/welcome-connecting.html'),
        name='welcome-connecting'),

    url(r'^welcome/data-import/$',
        WelcomeView.as_view(template_name='member/welcome-data-import.html'),
        name='welcome-data-import'),

    url(r'^welcome/profile/$',
        WelcomeView.as_view(template_name='member/welcome-profile.html'),
        name='welcome-profile'),

    # Public/shared views of member accounts
    url(r'^members/$',
        MemberListView.as_view(),
        name='member-list'),

    url(r'^members/page/(?P<page>\d+)/$',
        MemberListView.as_view(),
        name='member-list-paginated'),

    url(r'^member/(?P<slug>[A-Za-z_0-9]+)/$',
        MemberDetailView.as_view(),
        name='member-detail'),

    url(r'^member/(?P<slug>[A-Za-z_0-9]+)/email/$',
        EmailUserView.as_view(),
        name='member-email'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^raise-exception/$', ExceptionView.as_view()),
    ]
