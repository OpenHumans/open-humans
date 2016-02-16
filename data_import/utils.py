from time import time

from studies.models import BaseStudyUserData

from common.utils import app_label_to_app_config


def app_label_to_app_models(label):
    """
    Given an app's name, return its models.
    """
    return app_label_to_app_config(label).get_models()


def app_label_to_user_data_model(label):
    """
    Given an app name, return its UserData type.
    """
    for model in app_label_to_app_models(label):
        if (issubclass(model, BaseStudyUserData) or
                model.__name__ == 'UserData'):
            return model


def get_upload_path(instance, filename):
    """
    Construct the upload path for a upload-based data source.

    This path definition is currently unused but retained as a path consistent
    with the directory now used by Dropzone uploads, defined by get_upload_dir.
    """
    return '{}/{}'.format(
        get_upload_dir(source=instance, user=instance.user), filename)


def get_upload_dir(source, user):
    """
    Construct the upload directory for a upload-based data source.

    e.g. 23andMe uploaded files. These uploads are the original uploads from
    participants. With the exception of Data Selfie files, these will be
    processed and will not themselves be DataFiles (i.e. not intended to be
    shared or managed by participants.
    """
    return 'member/{}/uploaded-data/{}/{}/'.format(
        user.id, source._meta.app_label, int(time()))
