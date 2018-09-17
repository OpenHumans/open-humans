import logging

import mailchimp
import requests

from account.signals import email_confirmed

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from oauth2_provider.models import AccessToken

from common.utils import full_url, get_source_labels_and_configs
from private_sharing.models import ActivityFeed
from private_sharing.utilities import source_to_url_slug

from .models import Member

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Member)
def member_pre_save_cb(sender, instance, raw, **kwargs):
    """
    Subscribe or unsubscribe a user from Mailchimp.
    """
    if raw or settings.TESTING:
        return

    try:
        member = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if member.newsletter == instance.newsletter:
            return

    if not settings.MAILCHIMP_API_KEY:
        logger.warn('User changed email preference but no Mailchimp API key '
                    'has been specified, set MAILCHIMP_API_KEY.')

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
    if raw or not created or settings.TESTING or settings.ENV != 'production':
        return

    try:
        requests.post(settings.ZAPIER_WEBHOOK_URL, json={
            'type': 'member-created',
            'name': instance.name,
            'username': instance.user.username,
            'email': instance.primary_email.email,
        })
    except:  # pylint: disable=bare-except
        # monitoring should never interfere with the operation of the site
        pass


@receiver(post_save, sender=Member)
def member_post_save_activityfeed_event(
        sender, instance, created, raw, update_fields, **kwargs):
    """
    Record an 'account-created' ActivityFeed event when a Member signs up.
    """
    if raw or not created:
        return

    event = ActivityFeed(
        member=instance,
        action='created-account')
    event.save()


def send_welcome_email(email_address):
    """
    Send a welcome email. Rendered as a separate function to enable testing.
    """
    params = {
        'newsletter': email_address.user.member.newsletter,
        'add_data_url': full_url(reverse('add-data')),
        'explore_share_url': full_url(reverse('explore-share')),
        'public_sharing_url': full_url(reverse('public-data:home')),
        'data_management_url':
            full_url(reverse('my-member-data')),
    }

    plain = render_to_string('email/welcome.txt', params)
    html = render_to_string('email/welcome.html', params)

    send_mail('Welcome to Open Humans!',
              plain,
              settings.DEFAULT_FROM_EMAIL,
              [email_address.email],
              html_message=html)


@receiver(email_confirmed)
def email_confirmed_cb(email_address, **kwargs):
    """
    Send a user a welcome email once they've confirmed their email address.
    """
    send_welcome_email(email_address)
