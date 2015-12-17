# Taken from django-annoying only because the rest of django-annoying is not
# compatible with Django 1.7.

from django.db import IntegrityError
from django.db.models import OneToOneField
from django.db.models.fields.related_descriptors import (
    ReverseOneToOneDescriptor)


class AutoSingleRelatedObjectDescriptor(ReverseOneToOneDescriptor):
    """
    The descriptor that handles the object creation for an AutoOneToOneField.
    """
    def __get__(self, instance, instance_type=None):
        model = getattr(self.related, 'related_model', self.related.model)

        try:
            return (super(AutoSingleRelatedObjectDescriptor, self)
                    .__get__(instance, instance_type))
        except model.DoesNotExist:
            obj = model(**{self.related.field.name: instance})

            try:
                obj.save()
            except IntegrityError:
                # handle the race condition case by doing nothing and looking
                # up the object from the thread that won the save()
                pass

            # Don't return obj directly, otherwise it won't be added
            # to Django's cache, and the first 2 calls to obj.relobj
            # will return 2 different in-memory objects
            return (super(AutoSingleRelatedObjectDescriptor, self)
                    .__get__(instance, instance_type))


class AutoOneToOneField(OneToOneField):
    """
    OneToOneField creates related object on first call if it doesnt exist yet.
    Use it instead of original OneToOne field.

    example:

        class MyProfile(models.Model):
            user = AutoOneToOneField(User, primary_key=True)
            home_page = models.URLField(max_length=255, blank=True)
            icq = models.IntegerField(max_length=255, null=True)
    """
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(),
                AutoSingleRelatedObjectDescriptor(related))
