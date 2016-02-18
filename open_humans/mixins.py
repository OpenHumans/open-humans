from common.utils import app_label_to_user_data_model, get_source_labels


class SourcesContextMixin(object):
    """
    A mixin for adding context for connection sources to a template.
    """

    def get_context_data(self, **kwargs):
        context = super(SourcesContextMixin, self).get_context_data(**kwargs)

        context.update({label: app_label_to_user_data_model(label)
                        for label in get_source_labels()})

        return context
