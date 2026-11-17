import csv
import os
import re

from django.core.management.base import BaseCommand
from django.db.models import Count, Exists, OuterRef, Q

from data_import.models import DataFile
from open_humans.forms import BANNED_WORDS
from open_humans.models import Member
from private_sharing.forms import PROJECT_BANNED_WORDS
from private_sharing.models import DataRequestProject, DataRequestProjectMember

LINK_REGEX = r"https?|www\."


def matched_words(words, text):
    return sorted({w for w in words if re.search(w, text, re.I)})


def one_line(text, length=200):
    return " ".join(text.split())[:length]


class Command(BaseCommand):
    """
    A management command that lists accounts and projects that look like
    spam, for review. It only reads.
    """

    help = "Write CSV reports of likely spam accounts and unapproved projects"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            required=True,
            help="directory to write accounts.csv and projects.csv into",
        )

    def spam_projects(self):
        """
        Unapproved, active projects with their member counts and the spam
        signals found in their text.
        """
        projects = (
            DataRequestProject.objects.filter(approved=False, active=True)
            .select_related("coordinator__user")
            .annotate(
                members=Count(
                    "project_members",
                    filter=Q(
                        project_members__joined=True,
                        project_members__authorized=True,
                        project_members__revoked=False,
                    ),
                )
            )
            .order_by("id")
        )

        for project in projects:
            text = " ".join(
                [
                    project.name,
                    project.leader,
                    project.organization,
                    project.short_description,
                    project.long_description,
                ]
            )

            project.has_link = bool(re.search(LINK_REGEX, text, re.I))
            project.banned_words = matched_words(PROJECT_BANNED_WORDS, text)
            project.looks_like_spam = bool(project.has_link or project.banned_words)

            yield project

    def candidate_members(self, spam_coordinator_ids):
        """
        Active, non-staff members with no data files and no membership in an
        approved project, who either have a link or banned word in their name
        or coordinate a spam-looking project.
        """
        approved_memberships = DataRequestProjectMember.objects.filter(
            member=OuterRef("pk"),
            joined=True,
            authorized=True,
            revoked=False,
            project__approved=True,
        )

        return (
            Member.objects.filter(user__is_active=True, user__is_staff=False)
            .annotate(
                has_files=Exists(DataFile.objects.filter(user=OuterRef("user"))),
                has_approved_membership=Exists(approved_memberships),
            )
            .filter(has_files=False, has_approved_membership=False)
            .filter(
                Q(name__iregex=LINK_REGEX)
                | Q(name__iregex="|".join(BANNED_WORDS))
                | Q(pk__in=spam_coordinator_ids)
            )
            .select_related("user")
            .order_by("user__id")
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]

        projects = list(self.spam_projects())
        spam_coordinator_ids = {p.coordinator_id for p in projects if p.looks_like_spam}

        with open(os.path.join(output_dir, "projects.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "project_id",
                    "name",
                    "created",
                    "coordinator",
                    "members",
                    "has_link",
                    "banned_words",
                    "looks_like_spam",
                    "short_description",
                ]
            )

            for project in projects:
                writer.writerow(
                    [
                        project.id,
                        project.name,
                        project.created.date(),
                        project.coordinator.user.username,
                        project.members,
                        project.has_link,
                        " ".join(project.banned_words),
                        project.looks_like_spam,
                        one_line(project.short_description),
                    ]
                )

        candidates = 0

        with open(os.path.join(output_dir, "accounts.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "user_id",
                    "username",
                    "name",
                    "date_joined",
                    "last_login",
                    "name_has_link",
                    "name_banned_words",
                    "coordinates_spam_project",
                ]
            )

            for member in self.candidate_members(spam_coordinator_ids).iterator():
                candidates += 1

                writer.writerow(
                    [
                        member.user.id,
                        member.user.username,
                        member.name,
                        member.user.date_joined.date(),
                        member.user.last_login.date() if member.user.last_login else "",
                        bool(re.search(LINK_REGEX, member.name, re.I)),
                        " ".join(matched_words(BANNED_WORDS, member.name)),
                        member.pk in spam_coordinator_ids,
                    ]
                )

        self.stdout.write(
            "{} active members\n"
            "{} candidate accounts\n"
            "{} unapproved active projects, {} look like spam".format(
                Member.objects.filter(user__is_active=True).count(),
                candidates,
                len(projects),
                sum(p.looks_like_spam for p in projects),
            )
        )
