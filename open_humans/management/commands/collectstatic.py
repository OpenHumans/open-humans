import subprocess

from django.contrib.staticfiles.management.commands.collectstatic import \
    Command as BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('Not running gulp because of --dry-run')
        else:
            self.stdout.write('Starting gulp...')

        subprocess.Popen(['gulp build --production'],
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=self.stdout,
                         stderr=self.stderr).wait()

        super(Command, self).handle(*args, **options)
