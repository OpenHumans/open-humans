from django.apps import apps
from django.contrib.auth.models import User

from .models import BaseDataFile


# TODO: PERF: Gather list of models and retrieve them in one call? Add caching?
@property
def get_data_files(self):
    """
    Return a list with any matching DataFile-type objects.

    Various apps may contain "DataFile-type" objects, which are subclasses of
    data_import.BaseDataFile.
    """
    data_files = []

    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            if issubclass(model, BaseDataFile):
                data_files.extend(model.objects
                                  .filter(user_data__user=self)
                                  .select_related('public_data_access'))

    return data_files


# TODO: Decide if this should move to Member or not be a model method
User.add_to_class('data_files', get_data_files)
