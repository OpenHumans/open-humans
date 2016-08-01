from .processing import start_task


def start_task_for_source(user, source):
    """
    Create a retrieval task for the given user and datafile type.
    """
    user_data = getattr(user, source)

    if hasattr(user_data, 'refresh_from_db'):
        user_data.refresh_from_db()

    return start_task(user=user,
                      source=source,
                      task_params=user_data.get_retrieval_params())
