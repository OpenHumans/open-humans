from django.core.management.base import BaseCommand

from private_sharing.models import (
    DataRequestProject, OAuth2DataRequestProject, OnSiteDataRequestProject)


try:
    input = raw_input
except NameError:
    pass


class Command(BaseCommand):
    """
    A command for switching a project from oauth to onsite, and reverse.
    """

    help = 'Switch a project from on-site to oauth2, or reverse.'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--project',
                            dest='proj_id',
                            required=True,
                            help='Project ID that is going to be switched.')

        parser.add_argument('--convert',
                            choices=['oauth2onsite', 'onsite2oauth'],
                            dest='conv_type',
                            required=True,
                            help=('Conversion type: "oauth2onsite" or '
                                  '"onsite2oauth".'))

    def handle(self, *args, **options):
        if options['conv_type'] == 'oauth2onsite':
            proj_old = OAuth2DataRequestProject.objects.get(
                id=options['proj_id'])
            direction = ['OAuth2', 'On-site']
        elif options['conv_type'] == 'onsite2oauth':
            proj_old = OnSiteDataRequestProject.objects.get(
                id=options['proj_id'])
            direction = ['On-site', 'OAuth2']

        proj_parent = DataRequestProject.objects.get(id=options['proj_id'])
        conf = input('Switching project type for "{}" from {} to {}. Confirm '
                     '(Yes/No): '.format(proj_old, *direction))
        if conf.lower() != 'yes':
            print('Aborting.')
            return

        # Create a new project using the parent model values.
        fields = [f.name for f in proj_parent._meta.fields]
        values = {x: getattr(proj_old, x) for x in fields}
        if options['conv_type'] == 'oauth2onsite':
            proj_new = OnSiteDataRequestProject(**values)
        elif options['conv_type'] == 'onsite2oauth':
            proj_new = OAuth2DataRequestProject(**values)

        proj_new.save()
        proj_parent.save()
        out = proj_old.delete_without_cascade(keep_parents=True)
        print('Deleted the following:')
        print(out)
