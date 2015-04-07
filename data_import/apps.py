from django.apps import AppConfig


class DataImportConfig(AppConfig):
    """
    Configure the main Open Humans application.
    """
    name = 'data_import'
    verbose_name = 'Data Import'

    def ready(self):
        # Make sure our monkey patches are used

        # pylint: disable=unused-variable
        import data_import.monkey_patches  # noqa
