from common.utils import get_source_labels_and_names
from private_sharing.models import DataRequestProject


def get_source_labels_and_names_including_dynamic():
    """
    Same as get_source_labels_and_names but include direct-sharing projects.
    """
    sources = get_source_labels_and_names()

    sources += [('direct-sharing-{}'.format(project.id), project.name)
                for project in (DataRequestProject.objects
                                .filter(approved=True)
                                .exclude(returned_data_description=''))]

    return sorted(sources, key=lambda x: x[1].lower())
