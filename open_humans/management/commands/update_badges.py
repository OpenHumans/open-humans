from django.core.management.base import BaseCommand

from open_humans.models import Member


class Command(BaseCommand):
    """
    A management command for updating all user badges.
    """

    help = 'Update badges for all users'

    def handle(self, *args, **options):
        self.stdout.write('Updating badges')

        for member in Member.enriched.all():
            self.stdout.write('- {0}'.format(member.user.username))

            member.update_badges()

        self.stdout.write('Done')
