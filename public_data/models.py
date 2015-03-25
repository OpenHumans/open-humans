from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from common.fields import AutoOneToOneField
from open_humans.models import Member


class Participant(models.Model):
    """
    Represents a participant in the Public Data Sharing study.
    """
    member = AutoOneToOneField(Member,
                               related_name='public_data_participant')
    enrolled = models.BooleanField(default=False)
    signature = models.CharField(max_length=70)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    @property
    def public_files(self):
        """
        Return a list of all data_files that a participant is publicly sharing.
        """
        # Could be redundant, but double-checking is a good idea for this!
        # TODO: make this check into a decorator?
        if not self.enrolled:
            return []

        return [data_file
                for data_file in self.member.user.data_files
                if data_file.public_data_access().is_public
                # HIDE_23ANDME
                and data_file.source != 'twenty_three_and_me']

    def __unicode__(self):
        status = 'Not enrolled'

        if self.enrolled:
            status = 'Enrolled'

        return '%s:%s' % (self.member, status)


class PublicDataAccess(models.Model):
    """
    Keep track of public sharing for data files.

    data_file_model is expected to be a subclass of data_import.BaseDataFile.
    """
    data_file = GenericForeignKey('data_file_model', 'data_file_id')

    data_file_model = models.ForeignKey(ContentType)
    data_file_id = models.PositiveIntegerField()

    is_public = models.BooleanField(default=False)

    def download_url(self):
        return reverse('public-data:download', args=[self.id])

    def __unicode__(self):
        status = 'Private'

        if self.is_public:
            status = 'Public'

        return '%s:%s' % (self.data_file, status)


class AccessLog(models.Model):
    """
    Represents a download of a datafile.
    """
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True)
    public_data_access = models.ForeignKey(PublicDataAccess)

    def __unicode__(self):
        return '{} {} {} {}'.format(self.date, self.ip_address, self.user,
                                    self.public_data_access.data_file.file.url)


class WithdrawalFeedback(models.Model):
    """
    Keep track of any feedback a study participant gives when they withdraw
    from the study.
    """
    member = models.ForeignKey(Member)
    feedback = models.TextField(blank=True)
    withdrawal_date = models.DateTimeField(auto_now_add=True)
