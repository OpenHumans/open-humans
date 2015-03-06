from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.contrib import admin
# TODO: Move all uses of login_required to a mixin and add to views?
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from .views import (AuthorizationView,
                    DataRetrievalTaskDeleteView, ExceptionView,
                    MemberDetailView, MemberListView, MyMemberChangeEmailView,
                    MyMemberChangeNameView, MyMemberDashboardView,
                    MyMemberDatasetsView, MyMemberProfileEditView,
                    MyMemberSettingsEditView,
                    MyMemberSendConfirmationEmailView, OAuth2LoginView,
                    SignupView)

from . import api_urls

import activities.urls
import data_import.urls
import public_data.urls
import studies.urls_api
import studies.urls_study

urlpatterns = patterns(
    '',

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

    # Override oauth2/authorize to specify our own context data
    url(r'^oauth2/authorize/$', AuthorizationView.as_view(), name='authorize'),
    # The URLs used for the OAuth2 dance (e.g. requesting an access token)
    url(r'^oauth2/', include('oauth2_provider.urls',
                             namespace='oauth2_provider')),

    # URLs used for the Open Humans: Public Data Sharing study.
    url(r'^public-data/', include(public_data.urls, namespace='public-data')),

    # Simple pages
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'),
        name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),
    url(r'^community_guidelines/$',
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
    url(r'^terms/$',
        TemplateView.as_view(template_name='pages/terms.html'),
        name='terms-of-use'),
    url(r'^activities/$',
        TemplateView.as_view(template_name='pages/activities.html'),
        name='activities'),

    # Override because we use a custom form with custom view.
    url(r'^account/signup/$', SignupView.as_view(), name='account_signup'),
    # Custom view for prompting login when performing OAuth2 authorization
    url(r'^account/login/oauth2', OAuth2LoginView.as_view(),
        name='account_login_oauth2'),
    # This has to be after the overriden account/ URLs, not before
    url(r'^account/', include('account.urls')),

    # Member views of their own accounts.
    url(r'^member/me/$', login_required(MyMemberDashboardView.as_view()),
        name='my-member-dashboard'),
    url(r'^member/me/edit/$',
        login_required(MyMemberProfileEditView.as_view()),
        name='my-member-profile-edit'),
    url(r'^member/me/research-data/$',
        login_required(MyMemberDatasetsView.as_view()),
        name='my-member-research-data'),
    url(r'^member/me/research-data/delete/(?P<pk>[0-9]+)/$',
        login_required(DataRetrievalTaskDeleteView.as_view()),
        name='delete-data-retrieval-task'),
    url(r'^member/me/account-settings/$',
        login_required(MyMemberSettingsEditView.as_view()),
        name='my-member-settings'),
    url(r'^member/me/change-email/$',
        login_required(MyMemberChangeEmailView.as_view()),
        name='my-member-change-email'),
    url(r'^member/me/change-name/$',
        login_required(MyMemberChangeNameView.as_view()),
        name='my-member-change-name'),
    url(r'^member/me/send-confirmation-email/$',
        login_required(MyMemberSendConfirmationEmailView.as_view()),
        name='my-member-send-confirmation-email'),

    # Signup process prompts adding information to account.
    url(r'^member/me/signup-setup-1/$',
        login_required(MyMemberSettingsEditView.as_view(
            template_name='member/my-member-signup-setup-1.html',
            success_url=reverse_lazy('my-member-signup-setup-2'),
        )),
        name='my-member-signup-setup-1'),
    url(r'^member/me/signup-setup-2/$',
        login_required(MyMemberProfileEditView.as_view(
            template_name='member/my-member-signup-setup-2.html',
            success_url=reverse_lazy('my-member-research-data'),
            )),
        name='my-member-signup-setup-2'),

    # Public/shared views of member accounts
    url(r'^members/$',
        MemberListView.as_view(),
        name='member-list'),
    url(r'^member/(?P<slug>[A-Za-z_0-9]+)/$',
        MemberDetailView.as_view(),
        name='member-detail'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns(
        '',

        url(r'^raise-exception/$', ExceptionView.as_view()),
    )
