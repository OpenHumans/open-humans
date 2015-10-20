import logging

import mailchimp

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from oauth2_provider.models import AccessToken

from .models import Member

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Member)
def member_post_save_cb(sender, instance, created, raw, update_fields,
                        **kwargs):
    """
    Subscribe or unsubscribe a user from Mailchimp.
    """
    if raw:
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
            logger.warn('"%s" already subscribed', address)
        except mailchimp.Error as e:
            logger.error('A Mailchimp error occurred: %s, %s', e.__class__, e)
    else:
        try:
            mc.lists.unsubscribe(settings.MAILCHIMP_NEWSLETTER_LIST,
                                 {'email': address},
                                 send_goodbye=False,
                                 send_notify=False)
        except (mailchimp.ListNotSubscribedError,
                mailchimp.EmailNotExistsError):
            logger.warn('"%s" not subscribed', address)
        except mailchimp.Error as e:
            logger.error('A Mailchimp error occurred: %s, %s', e.__class__, e)


@receiver(post_save, sender=AccessToken)
def access_token_post_save_cb(sender, instance, created, raw, update_fields,
                              **kwargs):
    """
    Email a user to notify them of any new connections.
    """
    if raw or not created:
        return

    # only notify the user the first time they connect
    if AccessToken.objects.filter(application=instance.application,
                                  user=instance.user).count() > 1:
        return

    connection_name = instance.application.name

    params = {
        'user_name': instance.user.member.name,
        'connection_name': connection_name,
        'is_public_data_participant':
            instance.user.member.public_data_participant.enrolled,
        'public_data_sharing_url': reverse('public-data:home'),
        'research_data_url': reverse('my-member-research-data'),
    }

    plain = render_to_string('email/notify-connection.txt', params)
    html = render_to_string('email/notify-connection.html', params)

    send_mail('Open Humans Notification: {} Connected'.format(connection_name),
              plain,
              'admin@openhumans.com',
              # XXX: can we just use instance.user.email here?
              [instance.user.member.primary_email.email],
              html_message=html)
