import atexit
import futures
import os
import psutil
import subprocess
import traceback

from signal import SIGTERM

from django.contrib.staticfiles.management.commands.runserver import Command \
    as StaticfilesRunserverCommand
from django.core.management.base import CommandError

from ...utilities import get_env


class Command(StaticfilesRunserverCommand):
    """
    Subclass the RunserverCommand from Staticfiles to set up our gulp
    environment.
    """
    @staticmethod
    def gulp_exited_cb(future):
        if future.exception():
            print traceback.format_exc()

            children = psutil.Process().get_children(recursive=True)

            for child in children:
                print '>>> Killing pid {}'.format(child.pid)

                child.send_signal(SIGTERM)

            print '>>> Exiting'

            # It would be nice to be able to raise a CommandError or use
            # sys.kill here but neither of those stop the runserver instance
            # since we're in a thread. This method is used in django as well.
            os._exit(1)

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
        if not os.getenv('RUN_MAIN', False):
            pool = futures.ThreadPoolExecutor(max_workers=1)

            gulp_thread = pool.submit(self.start_gulp)
            gulp_thread.add_done_callback(self.gulp_exited_cb)

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

        @atexit.register
        def kill_gulp_process():
            self.stdout.write('>>> Closing gulp process')

            gulp_process.terminate()

        gulp_process.wait()

        if gulp_process.returncode != 0:
            raise CommandError('gulp exited unexpectedly')
