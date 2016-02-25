import logging

import mailchimp
import requests

from account.signals import email_confirmed

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from oauth2_provider.models import AccessToken
from social.apps.django_app.default.models import UserSocialAuth

from common.utils import full_url
from .models import Member

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Member)
def member_pre_save_cb(sender, instance, raw, **kwargs):
    """
    Subscribe or unsubscribe a user from Mailchimp.
    """
    if raw or settings.TESTING:
        return

    if not settings.MAILCHIMP_API_KEY:
        logger.warn('User changed email preference but no Mailchimp API key '
                    'has been specified, set MAILCHIMP_API_KEY.')

        return

    try:
        member = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if member.newsletter == instance.newsletter:
            return

    mc = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)

    try:
        address = instance.primary_email.email
    except AttributeError:
        # We're not sure why the callback is firing an extra time, before
        # SignupView.create_account runs (when email not yet saved).
        return

    if instance.newsletter:
        try:
            mc.lists.subscribe(settings.MAILCHIMP_NEWSLETTER_LIST,
                               {'email': address},
                               double_optin=False,
                               update_existing=True)
        except mailchimp.ListAlreadySubscribedError:
            logger.info('"%s" was already subscribed', address)
        except (mailchimp.Error, ValueError) as e:
            logger.error('A Mailchimp error occurred: %s, %s', e.__class__, e)
    else:
        try:
            mc.lists.unsubscribe(settings.MAILCHIMP_NEWSLETTER_LIST,
                                 {'email': address},
                                 send_goodbye=False,
                                 send_notify=False)
        except (mailchimp.ListNotSubscribedError,
                mailchimp.EmailNotExistsError):
            logger.info('"%s" was already unsubscribed', address)
        except (mailchimp.Error, ValueError) as e:
            logger.error('A Mailchimp error occurred: %s, %s', e.__class__, e)


@receiver(post_save, sender=Member)
def member_post_save_webhook_cb(
        sender, instance, created, raw, update_fields, **kwargs):
    """
    Send a webhook alert when a user signs up.
    """
    if raw or not created or settings.TESTING:
        return

    try:
        requests.post(settings.ZAPIER_WEBHOOK_URL, json={
            'type': 'member-created',
            'name': instance.name,
            'username': instance.user.username,
            'email': instance.primary_email.email,
        })
    except:
        # monitoring should never interfere with the operation of the site
        pass


def send_connection_email(user, connection_name):
    """
    Email a user to notify them of a new connection.
    """
    params = {
        'user_name': user.member.name,
        'connection_name': connection_name,
        'is_public_data_participant':
            user.member.public_data_participant.enrolled,
        'public_data_sharing_url': full_url(reverse('public-data:home')),
        'research_data_url': full_url(reverse('my-member-research-data')),
    }

    plain = render_to_string('email/notify-connection.txt', params)
    html = render_to_string('email/notify-connection.html', params)

    send_mail('Open Humans notification: {} connected'.format(connection_name),
              plain,
              settings.DEFAULT_FROM_EMAIL,
              [user.member.primary_email.email],
              html_message=html)


@receiver(post_save, sender=AccessToken)
def access_token_post_save_cb(sender, instance, created, raw, update_fields,
                              **kwargs):
    """
    Email a user to notify them of any new incoming connections.
    """
    if raw or not created:
        return

    # only notify the user the first time they connect
    if AccessToken.objects.filter(application=instance.application,
                                  user=instance.user).count() > 1:
        return

    send_connection_email(user=instance.user,
                          connection_name=instance.application.name)


@receiver(post_save, sender=UserSocialAuth)
def user_social_auth_post_save_cb(sender, instance, created, raw,
                                  update_fields, **kwargs):
    """
    Email a user to notify them of any new outgoing connections.
    """
    if raw or not created:
        return

    # only notify the user the first time they connect
    if UserSocialAuth.objects.filter(provider=instance.provider,
                                     user=instance.user).count() > 1:
        return

    send_connection_email(
        user=instance.user,
        connection_name=settings.PROVIDER_NAME_MAPPING[instance.provider])


@receiver(email_confirmed)
def email_confirmed_cb(email_address, **kwargs):
    """
    Send a user a welcome email once they've confirmed their email address.
    """
    params = {
        'newsletter': email_address.user.member.newsletter,
        'public_sharing_url': full_url(reverse('public-data:home')),
        'welcome_page_url': full_url(reverse('welcome')),
    }

    plain = render_to_string('email/welcome.txt', params)
    html = render_to_string('email/welcome.html', params)

    send_mail('Welcome to Open Humans!',
              plain,
              settings.DEFAULT_FROM_EMAIL,
              [email_address.email],
              html_message=html)
