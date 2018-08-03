import logging
from smtplib import SMTPRecipientsRefused

from account.hooks import AccountDefaultHookSet

logger = logging.getLogger(__name__)


class OpenHumansHookSet(AccountDefaultHookSet):
    """
    Override for sending the confirmation email that doesn't explode if the
    mailing process fails.
    """

    def send_confirmation_email(self, *args, **kwargs):
        try:
            super(OpenHumansHookSet, self).send_confirmation_email(*args,
                                                                   **kwargs)
        except SMTPRecipientsRefused:
            logger.warn('Unable to send confirmation mail.')
