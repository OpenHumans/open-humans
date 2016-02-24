from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from common import mixins

from . import label


# XXX: this model only adds properties to the User, it doesn't store any
# additional information. For that reason it doesn't really need to be a model.
class UserData(models.Model, mixins.UserSocialAuthUserData):
    """
    Used as key when a User has DataFiles for the RunKeeper activity.
    """

    class Meta:
        verbose_name = 'RunKeeper user data'
        verbose_name_plural = verbose_name

    provider = label

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    text_name = 'RunKeeper'
    href_connect = reverse_lazy('social:begin', args=('runkeeper',))
    href_next = reverse_lazy('activities:runkeeper:finalize-import')
    retrieval_url = reverse_lazy('activities:runkeeper:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, label)
