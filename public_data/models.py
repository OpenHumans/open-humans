from django.db import models

from common import fields
from open_humans.models import Member

from activities.twenty_three_and_me.models \
    import ActivityDataFile as Data23AndMe


class Participant(models.Model):
    member = models.OneToOneField(Member)
    enrolled = models.BooleanField(default=False)
    signature = models.CharField(max_length=70)
    enrollment_date = models.DateTimeField(auto_now_add=True)


class PublicSharing23AndMe(models.Model):
    """
    Manage public sharing for activities.twenty_three_and_me data files.
    """
    data_file = fields.AutoOneToOneField(Data23AndMe)
    is_public = models.BooleanField(default=False)
