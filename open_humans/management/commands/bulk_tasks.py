from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from data_import.tasks import start_or_postpone_task
from data_import.utils import (app_name_to_user_data_model,
                               app_name_to_data_file_model)

UserModel = get_user_model()


class Command(BaseCommand):
    """
    A management command for starting tasks for a given app or app and user.
    """

    help = 'Start all data processing tasks for a given app or app and user'

    def add_arguments(self, parser):
        parser.add_argument('-a, --app',
                            dest='app',
                            required=True,
                            help='the app to start tasks for')

        parser.add_argument('-u, --user',
                            dest='username',
                            required=False,
                            help=('an optional username, if specified then '
                                  'tasks are only started for that user'))

    def handle(self, *args, **options):
        AppModel = app_name_to_user_data_model(options['app'])
        DataFileModel = app_name_to_data_file_model(options['app'])

        user = None

        if options['username']:
            user = UserModel.objects.get(username=options['username'])

        if not AppModel:
            raise CommandError('Could not find UserData for "{}"'
                               .format(options['app']))

        data = AppModel.objects.all()

        if user:
            data = data.filter(user=user)

        def has_data(user_data):
            if hasattr(user_data, 'has_key_data'):
                return user_data.has_key_data

            return user_data.is_connected

        for user_data in [d for d in data if has_data(d)]:
            print 'starting task for {}'.format(user_data.user.username)

            start_or_postpone_task(user_data.user, DataFileModel)
