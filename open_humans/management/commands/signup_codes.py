import sys

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from account.models import EmailAddress, SignupCode


def code_from_email(email):
    """
    Create a SignupCode given an email address.
    """
    code = SignupCode.create(email=email,
                             expiry=7 * 24,
                             max_uses=1,
                             notes='Invited by signup_codes.py.')

    code.save()

    return code


class Command(BaseCommand):
    """
    Generate signup codes.
    """
    help = 'Generate signup codes.'
    args = '<filename>'
    option_list = BaseCommand.option_list + (
        make_option('--send',
                    action='store_true',
                    dest='send',
                    default=False,
                    help='Send an invitation email'),
    )

    def handle(self, *args, **options):
        if not len(args) == 1:
            raise CommandError('Please specify one filename.')

        try:
            with open(args[0]) as email_file:
                for email in email_file.read().splitlines():
                    if EmailAddress.objects.filter(email=email):
                        continue
                    code = code_from_email(email)

                    if options['send']:
                        code.send()

                    sys.stdout.write('Created code for "{}"\n'.format(email))
        except IOError:
            raise CommandError('File "{}" does not exist.'.format(args[0]))
