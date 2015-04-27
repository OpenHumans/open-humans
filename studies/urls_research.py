"""
URLs used by research.openhumans.org, where Researchers interact with the site.
"""

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.views.generic import TemplateView

from account.views import (
    ConfirmEmailView as AccountConfirmEmailView,
    LogoutView as AccountLogoutView,
    PasswordResetView as AccountPasswordResetView,
    PasswordResetTokenView as AccountPasswordResetTokenView)

# Our custom form enforces minimum password length.
from open_humans.forms import PasswordResetTokenForm

from .views import (ResearcherLoginView, ResearcherSignupView,
                    ResearcherConfirmEmailView)

urlpatterns = patterns(
    '',

    url(r'^$', TemplateView.as_view(template_name='research/home.html'),
        name='home'),

    # Account URLs.
    # Override to use custom form and view with added fields and methods.
    url(r'^account/signup/$', ResearcherSignupView.as_view(),
        name='account_signup'),
    url(r'^account/login/$', ResearcherLoginView.as_view(),
        name='account_login'),
    url(r"^account/confirm_email/(?P<key>\w+)/$",
        ResearcherConfirmEmailView.as_view(),
        name="account_confirm_email"),
    # Remaining: account views w/custom templates/forms, when possible.
    url(r'^account/logout/$', AccountLogoutView.as_view(
        template_name='research/account/logout.html'), name='account_logout'),
    url(r'^account/password/reset/$', AccountPasswordResetView.as_view(
        template_name='research/account/password_reset.html',
        template_name_sent='research/account/password_reset_sent.html'),
        name='account_password_reset'),
    url(r"^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$",
        AccountPasswordResetTokenView.as_view(
            template_name='research/account/password_reset_token.html',
            template_name_fail='research/account/password_reset_token_fail.html',
            form_class=PasswordResetTokenForm
        ), name="account_password_reset_token"),
    # Not actually part of accounts.
    url(r'^account/create/$',
        TemplateView.as_view(template_name='research/account/create.html'),
        name='account_create'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
