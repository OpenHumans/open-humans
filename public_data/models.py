from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from open_humans.models import Member


class Participant(models.Model):
    """
    Represents a participant in the Public Data Sharing study.
    """
    member = models.OneToOneField(Member,
                                  related_name='public_data_participant')
    enrolled = models.BooleanField(default=False)
    signature = models.CharField(max_length=70)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        status = "Not enrolled"
        if self.enrolled:
            status = "Enrolled"
        return "%s:%s" % (self.member, status)


class PublicDataStatus(models.Model):
    """
    Keep track of public sharing for data files.

    data_file_model is expected to be a subclass of data_import.BaseDataFile.
    """
    data_file_model = models.ForeignKey(ContentType)
    data_file_id = models.PositiveIntegerField()
    data_file = GenericForeignKey('data_file_model', 'data_file_id')
    is_public = models.BooleanField(default=False)

    def __unicode__(self):
        status = "Private"
        if self.is_public:
            status = "Public"
        return "%s:%s" % (self.data_file, status)
