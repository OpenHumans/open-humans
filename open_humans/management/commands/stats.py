# -*- coding: utf-8 -*-

import arrow

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from termcolor import colored

from open_humans.models import Member

UserModel = get_user_model()


class Command(BaseCommand):
    """
    Generate signup codes.
    """

    help = "Statistics on the last day(s) of users"
    args = ""

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", nargs="?", type=int, default=1, help="the number of days to show"
        )

    def handle(self, *args, **options):
        day_offset = options["days"] - 1

        end = arrow.now().span("day")[1]
        start = end.replace(days=-day_offset).span("day")[0]

        users = (
            UserModel.objects.all()
            .filter(date_joined__range=[start.datetime, end.datetime])
            .order_by("date_joined")
        )

        for user in users:
            self.stdout.write(
                "{} ({})".format(
                    user.username, arrow.get(user.date_joined).format("YYYY-MM-DD")
                )
            )

            try:
                for key, connection in list(user.member.connections.items()):
                    suffix = "no key data"

                    data = getattr(user, key).get_retrieval_params()

                    if key == "pgp" and "huID" in data:
                        suffix = data["huID"]

                    if key == "runkeeper" and "access_token" in data:
                        suffix = "access token present"

                    self.stdout.write(
                        "  {}: {} {}".format(
                            connection["verbose_name"], colored("✔", "green"), suffix
                        )
                    )
            except Member.DoesNotExist:
                pass

            self.stdout.write("")
