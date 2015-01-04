from django.contrib.auth.models import User
from django.db import models

from common import fields


class UserData(models.Model):
    user = fields.AutoOneToOneField(User, related_name='go_viral')


class GoViralId(models.Model):
    user_data = models.ForeignKey(UserData, related_name='go_viral_ids')

    value = models.CharField(primary_key=True, max_length=64)
