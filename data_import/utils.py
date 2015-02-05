import re

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from .models import BaseDataFile


def file_path_to_data_file_model(filepath):
    """
    Return DataFile model corresponding to a file's path.

    DataFile modules subclassed from data_import.BaseDataFile will have paths
    determined by their app name (see data_import.models.get_upload_path). This
    allows us to determine the originating app and model, given the file's
    storage path.
    """
    re_match = re.match(
        r"""member/                              # dir for member-related data
            (?P<username>[a-zA-Z0-9_@+-]{1,30})/ # User.username for member
            imported-data/                       # dir for member-imported data
            (?P<app_name>[a-z_]+)/               # DataFile's app name
            .+                                   # base file name
        """, filepath, flags=re.X)
    if not re_match:
        raise ValueError("Filepath '%s' does not match " % filepath +
                         "standard pattern for imported data!")
    for app_config in apps.get_app_configs():
        app_name = app_config.name.split('.')[-1]
        # Continue unless the file path matches the app's name.
        if not re_match.group('app_name') == app_name:
            continue
        for model in app_config.get_models():
            if issubclass(model, BaseDataFile):
                return model


def file_path_to_type_and_id(filepath):
    """
    Search all DataFile objects for match, return (ContentType, object_id)

    This uses file_path_to_data_file_model to determine the appropriate model,
    then finds the matching object for that model.
    """
    model = file_path_to_data_file_model(filepath)
    model_type = ContentType.objects.get_for_model(model)
    object_id = model.objects.get(file=filepath).id
    return (model_type, object_id)


def user_to_datafiles(user):
    """
    Return a list with any matching DataFile-type objects.

    Various apps may contain "DataFile-type" objects, which are subclasses of
    data_import.BaseDataFile.
    """
    data_files = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            if issubclass(model, BaseDataFile):
                for obj in model.objects.filter(user_data__user=user):
                    data_files.append(obj)
    return data_files
