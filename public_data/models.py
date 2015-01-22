from django.db import models

from open_humans.models import Member


class Participant(models.Model):
    member = models.OneToOneField(Member)
    enrolled = models.BooleanField(default=False)
    signature = models.CharField(max_length=70)
    enrollment_date = models.DateTimeField(auto_now_add=True)
