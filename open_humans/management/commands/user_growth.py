# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from open_humans.models import Member


class Command(BaseCommand):
    help = 'for plotting user growth'
    args = ''

    def handle(self, *args, **options):
        user_number = 1
        members = Member.objects.order_by('user__date_joined').filter(
            user__is_active=True
        )
        for member in members:
            print("{0}\t{1}".format(member.user.date_joined, user_number))
            user_number += 1
