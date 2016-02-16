from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.utils import get_upload_path


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the 23andme activity.
    """

    class Meta:
        verbose_name = '23andMe user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='twenty_three_and_me')

    # As of Feb 2016, we believe the the upload_to defined below is always
    # overridden by the DropzoneS3UploadFormView upload_to definition.
    # Maintaining here in case we use the version defined below in the future.
    genome_file = models.FileField(upload_to=get_upload_path, max_length=1024,
                                   null=True)

    text_name = '23andMe'
    href_connect = reverse_lazy('activities:23andme:upload')
    href_add_data = reverse_lazy('activities:23andme:upload')
    href_learn = 'https://www.23andme.com/'
    retrieval_url = reverse_lazy('activities:23andme:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, '23andme')

    @property
    def file_url(self):
        try:
            return self.genome_file.url
        except ValueError:
            return ''

    @property
    def is_connected(self):
        return self.file_url

    def disconnect(self):
        self.genome_file.delete()

    def get_retrieval_params(self):
        return {'file_url': self.file_url, 'username': self.user.username}
