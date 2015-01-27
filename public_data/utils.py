from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from common.utils import user_to_datafiles

from .models import PublicDataStatus


def get_public_files(user):
    """
    Return a list of all data_files that a participant is publicly sharing.
    """
    data_files = user_to_datafiles(user)
    public_data_files = []
    try:
        # Could be redundant, but double checking is a good idea for this!
        if user.member.public_data_participant.enrolled:
            public_statuses = datafiles_to_publicdatastatuses(data_files)
            for i in range(len(data_files)):
                if public_statuses[i].is_public:
                    public_data_files.append(data_files[i])
    except ObjectDoesNotExist:
        pass
    return public_data_files


def datafiles_to_publicdatastatuses(data_files):
    """
    Return a same-length list corresponding PublicDataStatus objects.
    """
    public_data_statuses = []
    for data_file in data_files:
        model_type = ContentType.objects.get_for_model(type(data_file))
        object_id = data_file.id
        obj, _ = PublicDataStatus.objects.get_or_create(
            data_file_model=model_type,
            data_file_id=object_id)
        public_data_statuses.append(obj)
    return public_data_statuses
