import os
import subprocess
import atexit
import signal

from django.contrib.staticfiles.management.commands.runserver import Command\
    as StaticfilesRunserverCommand


class Command(StaticfilesRunserverCommand):
    def inner_run(self, *args, **options):
        self.start_gulp()

        return super(Command, self).inner_run(*args, **options)

    def start_gulp(self):
        self.stdout.write('>>> Starting gulp')

        self.gulp_process = subprocess.Popen(
            ['gulp'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr,
        )

        self.stdout.write('>>> gulp process on pid {0}'
                          .format(self.gulp_process.pid))

        def kill_gulp_process(pid):
            self.stdout.write('>>> Closing gulp process')
            os.kill(pid, signal.SIGTERM)

        atexit.register(kill_gulp_process, self.gulp_process.pid)
