from django.core.mail.message import EmailMultiAlternatives

from celery import shared_task



@shared_task
def send_emails(emails,
                subject,
                headers=None,
                email_from='support@openhumans.org'):
    """
    Sends list of emails.  emails is a list of tuples in the
    form (to_address, message).
    """
    print('Sending {0} emails'.format(len(emails)))
    for to_address, email in emails:
        mail = EmailMultiAlternatives(
            subject,
            email,
            email_from,
            to_address,
            headers=headers)
        mail.send()
