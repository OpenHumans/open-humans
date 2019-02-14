from common.utils import get_activities, get_source_labels_and_configs


class SourcesContextMixin(object):
    """
    A mixin for adding context for connection sources to a template.
    """

    def get_context_data(self, **kwargs):
        context = super(SourcesContextMixin, self).get_context_data(**kwargs)

        context.update(
            {
                "sources": dict(get_source_labels_and_configs()),
                "activities": [
                    activity
                    for activity in get_activities()
                    if not activity[1].in_development
                ],
                "in_development_activities": [
                    activity
                    for activity in get_activities()
                    if activity[1].in_development
                ],
            }
        )

        return context
