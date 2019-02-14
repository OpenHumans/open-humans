from storages.backends.s3boto3 import S3Boto3Storage

TEN_MINUTES = 60 * 10


# pylint: disable=abstract-method
class PrivateStorage(S3Boto3Storage):
    """
    Private storage.
    """

    def __init__(self, *args, **kwargs):
        kwargs["acl"] = "private"
        kwargs["querystring_auth"] = True
        kwargs["querystring_expires"] = TEN_MINUTES

        super(PrivateStorage, self).__init__(*args, **kwargs)


# pylint: disable=abstract-method
class PublicStorage(S3Boto3Storage):
    """
    Public storage for user profile images.
    """

    def __init__(self, *args, **kwargs):
        kwargs["acl"] = "public-read"
        kwargs["querystring_auth"] = False

        super(PublicStorage, self).__init__(*args, **kwargs)
