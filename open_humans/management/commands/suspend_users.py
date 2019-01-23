from django.contrib.auth import get_user_model
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError

UserModel = get_user_model()


class Command(BaseCommand):
    """
    A management command for suspending one or more users.
    """

    help = 'Suspend users by username'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username',
                            dest='username',
                            required=False,
                            help=('one or more usernames, comma separated'))
        parser.add_argument('-i', '--id',
                            dest='id',
                            required=False,
                            help=('one or more ids, comma separated'))
        parser.add_argument('-e', '--email',
                            dest='email',
                            action='store_true',
                            help='send notification email')
        parser.add_argument('--skip-suspend',
                            dest='skip_suspend',
                            action='store_true',
                            help='mock run, skip performing actual suspension')

    def handle(self, *args, **options):
        users_to_suspend = []

        if options['username']:
            usernames = options['username'].split(',')
            for username in usernames:
                try:
                    users_to_suspend.append(
                        UserModel.objects.get(username=username))
                except UserModel.DoesNotExist:
                    raise CommandError('Username "{}" does not exist!'
                                       .format(username))

        if options['id']:
            ids = options['id'].split(',')
            for id_str in ids:
                try:
                    users_to_suspend.append(
                        UserModel.objects.get(id=int(id_str)))
                except UserModel.DoesNotExist:
                    raise CommandError('User ID "{}" does not exist!'
                                       .format(id_str))

        if options['email']:
            self.email_notification(users_to_suspend)

        for user in users_to_suspend:
            if not options['skip_suspend']:
                user.is_active = False
                user.save()
            print('{} (ID: {}) is suspended.'.format(user.username, user.id))

    def _body_text(self, username):
        body_text = """{0},

Your Open Humans account (username: "{0}") has been suspended for
misuse of the platform. We want to ensure that the site is not misused,
e.g. for advertising spam.

If this was done in error, please reply to this email to let us know!
There are sometimes mistakes in detecting spam accounts and other abuses.

Sincerely,

Open Humans
""".format(username)
        return body_text

    def email_notification(self, users):
        subject = 'Open Humans: Account suspension notification'

        messages = []
        for user in users:
            body_text = self._body_text(user.username)
            message = EmailMultiAlternatives(
                subject, body_text, None, [user.email])
            messages.append(message)

        connection = get_connection()
        connection.send_messages(messages)
