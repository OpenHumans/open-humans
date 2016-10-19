import random
import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from common.utils import app_label_to_user_data_model
from data_import.processing import start_task

UserModel = get_user_model()


class Command(BaseCommand):
    """
    A management command for starting tasks for a given app or app and user.
    """

    help = 'Start all data processing tasks for a given app or app and user'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--app',
                            dest='app',
                            required=True,
                            help='the app to start tasks for')

        parser.add_argument('-u', '--user',
                            dest='username',
                            required=False,
                            help=('an optional username, if specified then '
                                  'tasks are only started for that user'))

        parser.add_argument('-f', '--force',
                            dest='force',
                            required=False,
                            action='store_true',
                            help=('Use with caution! Forces reprocessing even '
                                  'if "should_update" in the processing server'
                                  ' evaluates as false.'))

        parser.add_argument('-d', '--delay',
                            dest='delay',
                            required=False,
                            help='Added delay (seconds) between each task.')

    def handle(self, *args, **options):
        UserDataModel = app_label_to_user_data_model(options['app'])

        user = None

        if options['username']:
            user = UserModel.objects.get(username=options['username'])

        if not UserDataModel:
            raise CommandError('Could not find UserData for "{}"'
                               .format(options['app']))

        if hasattr(UserDataModel, 'objects'):
            data = list(UserDataModel.objects.all())

            if user:
                data = list(data.filter(user=user))
        else:
            UserDataModel.user = user
            data = list(UserDataModel.to_list())

        def has_data(user_data):
            if hasattr(user_data, 'has_key_data'):
                return user_data.has_key_data

            return user_data.is_connected

        random.shuffle(data)
        for user_data in [d for d in data if has_data(d)]:
            self.stdout.write('starting task for {}'.format(
                user_data.user.username))

            if user_data.user.member.primary_email.verified:
                start_task(user_data.user, options['app'],
                           force=options['force'])

                print '- task was started'
            else:
                print '- task was not started (unverified email)'

            if options['delay']:
                time.sleep(int(options['delay']))
