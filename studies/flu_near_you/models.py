from django.contrib.auth.models import User
from django.db import models

from common import fields


class UserData(models.Model):
    user = fields.AutoOneToOneField(User, related_name='flu_near_you')
