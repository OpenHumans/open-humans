"""
URLs used by research.openhumans.org, where Researchers interact with the site.
"""

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.views.generic import TemplateView

from account.views import (ConfirmEmailView as AccountConfirmEmailView,
                           LogoutView as AccountLogoutView)

from .views import (ResearcherLoginView, ResearcherSignupView,
                    ResearcherConfirmEmailView)

urlpatterns = patterns(
    '',

    url(r'^$', TemplateView.as_view(template_name='research/home.html'),
        name='home'),
    # Override to use custom form and view with added fields and methods.
    url(r'^account/signup/$', ResearcherSignupView.as_view(),
        name='account_signup'),
    url(r'^account/login/$', ResearcherLoginView.as_view(),
        name='account_login'),
    # Can't override template wo/ overriding view for this one.
    url(r"^account/confirm_email/(?P<key>\w+)/$",
        ResearcherConfirmEmailView.as_view(),
        name="account_confirm_email"),
    # Remaining account overrides: custom templates but using account views
    url(r'^account/logout/$', AccountLogoutView.as_view(
        template_name='research/account/logout.html'), name='account_logout'),
    url(r'^account/password/reset/$', TemplateView.as_view(
        template_name='research/account/password_reset.html'),
        name='account_password_reset'),
    # Not actually part of accounts.
    url(r'^account/create/$',
        TemplateView.as_view(template_name='research/account/create.html'),
        name='account_create'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
