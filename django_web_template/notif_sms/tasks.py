import uuid
import json

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger

from notif_sms.external_wrapper import SmsClientWrapper, SmsClientType


logger = get_task_logger(__name__)


@shared_task(
    name="task_send_sms",
    queue="send_sms",
    bind=True,
    max_retries=3,
    soft_time_limit=10,)
def task_send_sms(self, user_external_id: str, mob_num: str, sms_mess: str, sender_id: str = None,
                  is_transactional: bool = True, retry_required: bool = True):
    try:

        SmsClientWrapper(SmsClientType.ANY).send_sms(
            user_external_id, mob_num, sms_mess, sender_id, is_transactional)
    except SoftTimeLimitExceeded as e:
        logger.error("{0}-{1}-{2}".format(__name__, "task_send_sms", str(e)))
        if retry_required:
            raise self.retry(countdown=3 ** self.request.retries, exc=e)
        else:
            raise
    except Exception as e:
        logger.error("{0}-{1}-{2}".format(__name__, "task_send_sms", str(e)))
        if retry_required:
            raise self.retry(countdown=3 ** self.request.retries, exc=e)
        else:
            raise


@shared_task(
    bind=True,
    max_retries=2,
    name="task_handle_sms_delivery_cb",
    queue="sms_report")
def task_handle_sms_delivery_cb(self, cb_data, client_type: SmsClientType):
    try:
        SmsClientWrapper(client_type).handle_report_data(cb_data)
    except Exception as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_handle_sms_delivery_cb", str(e)))
        self.retry(countdown=10 ** self.request.retries, exc=e)
