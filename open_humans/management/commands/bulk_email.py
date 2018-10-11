import csv
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

    help = ('Bulk email Open Humans members. Requires three template files, '
            'specified as a basename by the -t option, and a file of emails '
            '(plus optional merge data), specified by the -e option. The '
            'email file should be a csv with a header; the "email" column '
            'designates emails, and is used to provide a "user" (User) object '
            'for template context data. Other columns are mapped to context '
            'data (e.g. "mytoken" is used to fill {{ mytoken }} in the '
            'template). The template basename should have three files '
            'available: .txt, .html, and .subject files.')

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

        email_data = []
        with open(email_file, 'r') as f:
            csvreader = csv.reader(f)
            headers = next(csvreader)
            if 'email' not in headers:
                raise ValueError(
                    "{0} does not have 'email' as one of the header row "
                    'columns.'.format(options['email_file']))
            if 'user' in headers:
                raise ValueError(
                    "Sorry, 'user' isn't allowed in the header, this is used "
                    'to pass a User object to template as context.')
            for row in csv.reader(f):
                data = {}
                for i in range(len(headers)):
                    data[headers[i]] = row[i]
                email_data.append(data)

        name = os.path.basename(template)

        messages = []

        for data in email_data:
            print(data)

            user = UserModel.objects.get(email=data['email'])
            context = {'user': user}
            for item in data.keys():
                context[item] = data[item]
            subject = render_to_string('{0}.subject'.format(name),
                                       context).strip()
            plain = render_to_string('{0}.txt'.format(name), context)
            html = render_to_string('{0}.html'.format(name), context)

            messages.append((subject, plain, html, None, (data['email'],)))

        send_mass_html_mail(messages)
