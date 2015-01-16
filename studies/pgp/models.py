from django.contrib.auth.models import User
from django.db import models

from common import fields


class UserData(models.Model):
    user = fields.AutoOneToOneField(User, related_name='pgp')


class HuId(models.Model):
    user_data = models.ForeignKey(UserData, related_name='huids')

    value = models.CharField(primary_key=True, max_length=64)
