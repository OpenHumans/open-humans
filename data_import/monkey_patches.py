from django.contrib.auth import get_user_model

from .models import DataFile


@property
def get_data_files(self):
    """
    Return a list with any matching DataFile-type objects.
    """
    return DataFile.objects.filter(user=self)


UserModel = get_user_model()

# TODO: Decide if this should move to Member or not be a model method
UserModel.add_to_class('data_files', get_data_files)
