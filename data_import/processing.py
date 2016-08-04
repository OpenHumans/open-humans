import logging
import urlparse

import requests

from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from common.utils import full_url

from .utils import get_upload_dir

logger = logging.getLogger(__name__)


def start_task(user, source, task_params):
    task_url = '{}/'.format(
        urlparse.urljoin(settings.DATA_PROCESSING_URL, source))

    task_params.update({
        'oh_user_id': user.id,
        'oh_member_id': user.member.member_id,
        'oh_update_url': full_url('/data-import/task-update/'),
        's3_key_dir': get_upload_dir(source),
        's3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
    })

    try:
        task_req = requests.post(
            task_url,
            params={'key': settings.PRE_SHARED_KEY},
            json={'task_params': task_params})
    except requests.exceptions.RequestException:
        logger.error('Error in sending request to data processing')
        logger.error('These were the task params: %s', task_params)

        error_message = 'Error in call to Open Humans Data Processing.'

    if 'task_req' in locals() and not task_req.status_code == 200:
        logger.error('Non-200 response from data processing')
        logger.error('These were the task params: %s', task_params)

        error_message = 'Open Humans Data Processing not returning 200.'

    if 'error_message' in locals():
        if not settings.TESTING:
            client.captureMessage(error_message, error_data=task_params)

        return 'error'


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
