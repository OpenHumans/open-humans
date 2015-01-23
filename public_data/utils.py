"""
SLUG_TO_SHARING_MODE - a dict with:
    key: string corresponding to the study's or activity's identifying slug
        in its file storage path, i.e. the 'slugID' in this general pattern:
        member/{username}/{activity-data or study-data}/{slugID}/{filename}
    value: the model tracking public sharing status from this module's
        models.py. Names for these models should start with "PublicSharing",
        e.g. "PublicSharing23andme".

get_public_files - a function. See its associated docstring for details.
"""
from .models import PublicSharing23AndMe

SLUG_TO_SHARING_MODEL = {
    'twenty_three_and_me': PublicSharing23AndMe,
}

def get_public_files(member):
    """
    Returns a list of study/activity data files 'public' for a given Member.

    Single argument: a Member object from open_humans/models

    Returns: A list of tuples: (activity or study data file, identifying slug)
        The activity or study data files are Django File objects corresponding
        to data files from activities or studies whose public sharing status
        is managed by the PublicSharing* models within SLUG_TO_SHARING_MODEL.
    """
    public_files = []
    # I tried to use itertools.chain to flatten, didn't work for me.
    sharing_model_data = [(SLUG_TO_SHARING_MODEL[x].objects.filter(
            data_file__user_data__user__member=member), x)
        for x in SLUG_TO_SHARING_MODEL]
    for item in sharing_model_data:
        sharing_model_queryset = item[0]
        slug = item[1]
        for sharing_model in sharing_model_queryset:
            if sharing_model.is_public:
                public_files.append((sharing_model.data_file, slug))
    return public_files
