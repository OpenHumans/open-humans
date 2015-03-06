from django.contrib.auth.models import User
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask

from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    user = fields.AutoOneToOneField(User, related_name='american_gut')

    def get_retrieval_params(self):
        barcodes = [barcode.value for barcode in
                    Barcode.objects.filter(user_data=self)]
        app_task_params = {'barcodes': barcodes}
        return app_task_params

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        connected = self.is_connected
        if connected:
            barcodes = Barcode.objects.filter(user_data=self)
            if barcodes:
                return True
        return False


class Barcode(models.Model):
    user_data = models.ForeignKey(UserData, related_name='barcodes')

    value = models.CharField(primary_key=True, max_length=64)


class DataFile(BaseDataFile):
    """
    Storage for an American Gut data file.
    """
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_american_gut')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'american_gut', self.file)
