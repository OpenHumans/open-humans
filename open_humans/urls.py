from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from .views import (SignupView, ExceptionView,
                    MemberDetailView, MemberListView, MyMemberChangeEmailView,
                    MyMemberDashboardView, MyMemberDatasetsView,
                    MyMemberProfileEditView,
                    MyMemberSettingsEditView)

from . import api_urls

import studies.urls
import activities.urls

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    # Include the various APIs here
    url(r'^api/', include(studies.urls)),
    url(r'^api/', include(api_urls)),

    # URLs used for activity-related interactions.
    # Authentication with python-social-auth reqs top-level 'social' namespace.
    url(r'^activity/auth/',
        include('social.apps.django_app.urls', namespace='social')),
    url(r'^activity/', include(activities.urls, namespace='activities')),

    # The URLs used for the OAuth2 dance (e.g. requesting an access token)
    url(r'^oauth2/', include('oauth2_provider.urls',
                             namespace='oauth2_provider')),

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
    url(r'^activities/$',
        TemplateView.as_view(template_name='pages/activities.html'),
        name='activities'),
    # Login and signup modals should return to this page. I tried
    # reverse_lazy but that led to an recursion error.  - Madeleine
    url(r'^public-data-sharing/$',
        TemplateView.as_view(template_name='pages/public-data-sharing.html'),
        {'redirect_field_name': 'next',
         'redirect_field_value': '/public-data-sharing/'},
        name='public-data-sharing'),

    # Override because we use a custom form with custom view.
    url(r'^account/signup/$', SignupView.as_view(), name='account_signup'),
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
    url(r'^member/me/account-settings/$',
        login_required(MyMemberSettingsEditView.as_view()),
        name='my-member-settings'),
    url(r'^member/me/change-email/$',
        login_required(MyMemberChangeEmailView.as_view()),
        name='my-member-change-email'),

    # Signup process prompts adding information to account.
    url(r'^member/me/signup-setup-1/$',
        login_required(MyMemberSettingsEditView.as_view(
            template_name='member/my-member-signup-setup-1.html',
            success_url=reverse_lazy('my-member-signup-setup-2'),
            initial={'submit_value': 'Save and continue'},
        )),
        name='my-member-signup-setup-1'),
    url(r'^member/me/signup-setup-2/$',
        login_required(MyMemberProfileEditView.as_view(
            template_name='member/my-member-signup-setup-2.html',
            success_url=reverse_lazy('my-member-research-data'),
            initial={'submit_value': 'Save and continue'},
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
