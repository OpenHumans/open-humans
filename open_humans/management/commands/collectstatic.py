import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('>>> Starting gulp')

        subprocess.Popen(['gulp build --production'],
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=self.stdout,
                         stderr=self.stderr).wait()
