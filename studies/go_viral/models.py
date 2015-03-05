from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    user = fields.AutoOneToOneField(User, related_name='go_viral')

    def get_retrieval_params(self):
        # TODO: We assume a single GoViral ID.
        # If true, change GoViralId.user_data to OneToOne?
        # If false, change data processing?
        go_viral_id = (GoViralId.objects.filter(user_data=self)[0].id)

        return {
            'access_token': settings.GO_VIRAL_MANAGEMENT_TOKEN,
            'go_viral_id': go_viral_id
        }


class GoViralId(models.Model):
    user_data = models.ForeignKey(UserData, related_name='go_viral_ids')

    value = models.CharField(primary_key=True, max_length=64)


class DataFile(BaseDataFile):
    """
    Storage for an GoViral data file.
    """
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_go_viral')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'go_viral', self.file)
