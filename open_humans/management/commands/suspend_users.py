from django.contrib.auth import get_user_model
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

        for user in users_to_suspend:
            user.is_active = False
            user.save()
            print('{} (ID: {}) is suspended.'.format(user.username, user.id)
