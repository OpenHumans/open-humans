import os

from django.contrib.auth import get_user_model
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

UserModel = get_user_model()


def full_path(path):
    """
    Get an absolute path.
    """
    if path[0] == '/':
        return path

    return os.path.realpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', '..', path))


def send_mass_html_mail(datatuple, fail_silently=False, connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    """
    connection = get_connection(fail_silently=fail_silently)

    messages = []

    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)

        message.attach_alternative(html, 'text/html')
        messages.append(message)

    return connection.send_messages(messages)


class Command(BaseCommand):
    """
    A management command for bulk emailing Open Humans users.
    """

    help = ('Bulk email Open Humans members. Requires a template file, '
            'specified as a basename by the -t option, and a file of emails, '
            'specified by the -e option. The email file should contain one '
            'email per line. The template basename should have a .txt, .html, '
            'and .subject file.')

    def add_arguments(self, parser):
        parser.add_argument('-t, --template',
                            dest='template',
                            required=True,
                            help="the template files' basename")

        parser.add_argument('-e, --emails',
                            dest='email_file',
                            required=True,
                            help='the email list file')

    def handle(self, *args, **options):
        template = full_path(options['template'])
        email_file = full_path(options['email_file'])

        with open(email_file) as f:
            emails = f.read().splitlines()

        path = (os.path.dirname(template),)
        name = os.path.basename(template)

        messages = []

        for email in emails:
            self.stdout.write(email)

            user = UserModel.objects.get(email=email)
            data = {'user': user}

            subject = render_to_string('{}.subject'.format(name), data,
                                       dirs=path).strip()
            plain = render_to_string('{}.txt'.format(name), data, dirs=path)
            html = render_to_string('{}.html'.format(name), data, dirs=path)

            messages.append((subject, plain, html, None, (email,)))

        send_mass_html_mail(messages)
