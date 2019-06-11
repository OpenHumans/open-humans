from collections import OrderedDict
from itertools import groupby

from django.db import models
from django.db.models import F

from common.fields import AutoOneToOneField
from open_humans.models import Member
from private_sharing.models import (
    DataRequestProjectMember,
    ProjectDataFile,
    id_label_to_project,
)


def is_public(member, source):
    """
    Return whether a given member has publicly shared the given source.
    """
    project = id_label_to_project(source)
    return bool(
        member.public_data_participant.publicdataaccess_set.filter(
            project_membership__project=project, is_public=True
        )
    )


def public_count(project):
    """
    Get number of users publicly sharing a project's data.
    """
    count = (
        PublicDataAccess.objects.filter(
            project_membership__project=project,
            # Filter to only count members with datafiles for this project.
            is_public=True,
            project_membership__project__in=F(
                "project_membership__member__user__datafiles__"
                "parent_project_data_file__direct_sharing_project"
            ),
        )
        .distinct()
        .count()
    )
    return count


class Participant(models.Model):
    """
    Represents a participant in the Public Data Sharing study.
    """

    member = AutoOneToOneField(
        Member, related_name="public_data_participant", on_delete=models.CASCADE
    )
    enrolled = models.BooleanField(default=False)

    def _files_for_project(self, project):
        return ProjectDataFile.objects.filter(
            user=self.member.user, direct_sharing_project=project
        ).exclude(completed=False)

    @property
    def public_data_w_vis_membership_by_proj(self):
        vis_projs_w_public_data = [
            pda.project_membership.project
            for pda in self.publicdataaccess_set.filter(
                is_public=True, project_membership__visible=True
            )
        ]
        files = self.member.user.datafiles.filter(
            parent_project_data_file__direct_sharing_project__in=vis_projs_w_public_data
        ).order_by("parent_project_data_file__direct_sharing_project", "created")
        grouped_by_project = groupby(
            files, key=lambda x: x.parent_project_data_file.direct_sharing_project
        )
        files_by_project = OrderedDict()
        for proj, files in grouped_by_project:
            files_by_project[proj] = []
            for file in files:
                files_by_project[proj].append(file)
        return files_by_project

    def __str__(self):
        status = "Enrolled" if self.enrolled else "Not enrolled"

        return str("{0}:{1}").format(self.member, status)


class PublicDataAccess(models.Model):
    """
    Keep track of public sharing for a data source.

    The data source is the DataRequestProject identified by the project_membership.
    """

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    project_membership = models.OneToOneField(
        DataRequestProjectMember, on_delete=models.CASCADE
    )
    is_public = models.BooleanField(default=False)

    def __str__(self):
        status = "Private"

        if self.is_public:
            status = "Public"

        return str("{0}:{1}:{2}").format(
            self.participant.member.user.username,
            self.project_membership.project.name,
            status,
        )


class WithdrawalFeedback(models.Model):
    """
    Keep track of any feedback a study participant gives when they withdraw
    from the study.
    """

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    feedback = models.TextField(blank=True)
    withdrawal_date = models.DateTimeField(auto_now_add=True)
