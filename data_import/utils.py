from uuid import uuid1


def get_upload_path(instance, filename):
    """
    Construct a unique S3 path for a source and filename.
    """
    return '{0}{1}'.format(get_upload_dir(instance=instance), filename)


def get_source(instance):
    """
    Given an instance, return the associated source.
    """
    if hasattr(instance, 'source'):
        return instance.source

    if hasattr(instance, '_meta'):
        return instance._meta.app_label

    return instance


def get_upload_dir(instance):
    """
    Construct a unique S3 key for a source.
    """
    return 'member-files/{0}/{1}/'.format(get_source(instance), str(uuid1()))
