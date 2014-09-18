from django.contrib.auth.models import User
from django.db import models


class UserData(models.Model):
    user = models.OneToOneField(User, related_name='american_gut')


class Barcode(models.Model):
    value = models.CharField(max_length=64)
    user_data = models.ForeignKey(UserData, related_name='barcodes')
