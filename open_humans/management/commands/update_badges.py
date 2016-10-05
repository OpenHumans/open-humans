from django.core.management.base import BaseCommand

from common.activities import personalize_activities_dict

from open_humans.models import Member


class Command(BaseCommand):
    """
    A management command for updating all user badges.
    """

    help = 'Update badges for all users'

    def handle(self, *args, **options):
        self.stdout.write('Updating badges')

        badge_data = {k: v['badge']
                      for k, v in personalize_activities_dict(
                      only_active=False).items()}

        for member in Member.enriched.all():
            self.stdout.write('- {0}'.format(member.user.username))

            member.badges = []

            # Badges for activities and deeply integrated studies, e.g. PGP,
            # RunKeeper
            for label, _ in member.connections.items():
                member.badges.append(badge_data[label])

            project_memberships = (member.datarequestprojectmember_set
                                   .filter(project__approved=True)
                                   .filter_active())

            # Badges for DataRequestProjects
            for membership in project_memberships:
                member.badges.append(badge_data[membership.project.id_label])

            # The badge for the Public Data Sharing Study
            if member.public_data_participant.enrolled:
                member.badges.append(badge_data['public_data_sharing'])

            member.save()

        self.stdout.write('Done')
