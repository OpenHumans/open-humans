import logging

import mailchimp

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Member

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Member)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
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
    address = instance.primary_email.email

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
                                 delete_member=True,
                                 send_goodbye=False,
                                 send_notify=False)
        except (mailchimp.ListNotSubscribedError,
                mailchimp.EmailNotExistsError):
            logger.warn('"%s" not subscribed', address)
        except mailchimp.Error as e:
            logger.error('A Mailchimp error occurred: %s, %s', e.__class__, e)
