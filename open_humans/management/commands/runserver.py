import atexit
import subprocess

from django.contrib.staticfiles.management.commands.runserver import Command \
    as StaticfilesRunserverCommand
from django.core.management.base import CommandError


class Command(StaticfilesRunserverCommand):
    def inner_run(self, *args, **options):
        self.start_gulp()

        return super(Command, self).inner_run(*args, **options)

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
