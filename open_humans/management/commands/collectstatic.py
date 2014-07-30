import subprocess

from django.contrib.staticfiles.management.commands.collectstatic import \
    Command as BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('>>> Starting gulp')

        subprocess.Popen(['gulp build --production'],
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=self.stdout,
                         stderr=self.stderr).wait()
