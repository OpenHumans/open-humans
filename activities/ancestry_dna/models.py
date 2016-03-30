from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.utils import get_upload_path

from . import label


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the AncestryDNA activity.
    """

    class Meta:
        verbose_name = 'AncestryDNA user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    genome_file = models.FileField(upload_to=get_upload_path, max_length=1024,
                                   null=True)

    text_name = 'AncestryDNA'
    href_connect = reverse_lazy('activities:ancestry-dna:upload')
    href_add_data = reverse_lazy('activities:ancestry-dna:upload')
    href_learn = 'http://dna.ancestry.com/'
    retrieval_url = reverse_lazy(
        'activities:ancestry-dna:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, 'AncestryDNA')

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
