from storages.backends.s3 import S3Storage

TEN_MINUTES = 60 * 10


# pylint: disable=abstract-method
class PrivateStorage(S3Storage):
    """
    Private storage.
    """

    def __init__(self, *args, **kwargs):
        kwargs["default_acl"] = "private"
        kwargs["querystring_auth"] = True
        kwargs["querystring_expire"] = TEN_MINUTES

        super(PrivateStorage, self).__init__(*args, **kwargs)


# pylint: disable=abstract-method
class PublicStorage(S3Storage):
    """
    Public storage for user profile images.
    """

    def __init__(self, *args, **kwargs):
        kwargs["default_acl"] = "public-read"
        kwargs["querystring_auth"] = False

        super(PublicStorage, self).__init__(*args, **kwargs)
