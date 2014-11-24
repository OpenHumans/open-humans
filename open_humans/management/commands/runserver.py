import atexit
import os
import subprocess

from django.contrib.staticfiles.management.commands.runserver import Command \
    as StaticfilesRunserverCommand
from django.core.management.base import CommandError

from ...utilities import get_env


class Command(StaticfilesRunserverCommand):
    def handle(self, *args, **options):
        env = dict(get_env())

        # XXX: In Django 1.8 this changes to:
        # if 'PORT' in env and not options.get('addrport'):
        #     options['addrport'] = env['PORT']

        if 'PORT' in env and not args:
            args = (env['PORT'],)

        # We're subclassing runserver, which spawns threads for its
        # autoreloader with RUN_MAIN set to true, we have to check for
        # this to avoid running gulp twice.
        if not os.environ.get('RUN_MAIN', False):
            self.start_gulp()

        return super(Command, self).handle(*args, **options)

    def start_gulp(self):
        self.stdout.write('>>> Starting gulp')

        gulp_process = subprocess.Popen(
            ['gulp'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr)

        if gulp_process.poll() is not None:
            raise CommandError('gulp failed to start')

        self.stdout.write('>>> gulp process on pid {0}'
                          .format(gulp_process.pid))

        def kill_gulp_process(gulp_process):
            self.stdout.write('>>> Closing gulp process')

            gulp_process.terminate()

        atexit.register(kill_gulp_process, gulp_process)
