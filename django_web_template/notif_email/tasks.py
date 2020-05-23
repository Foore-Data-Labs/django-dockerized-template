import uuid
import json

from django.conf import settings
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger

from notif_email.external_wrapper import EmailClientWrapper, EmailClientType


logger = get_task_logger(__name__)


@shared_task(
    name="task_send_simple_email",
    queue="email_queue",
    bind=True,
    max_retries=3,
    soft_time_limit=10,)
def task_send_simple_email(self, user_external_id: str, sender_email: str, sender_name: str,
                           to_email: str, subject: str, plain_text_content: str, html_content: str, retry_required: bool = True):
    try:
        EmailClientWrapper(EmailClientType.ANY).send_email(user_external_id, sender_email, sender_name,
                                                           to_email, subject, plain_text_content, html_content)
    except SoftTimeLimitExceeded as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_simple_email", str(e)))
        if retry_required:
            raise self.retry(countdown=3 ** self.request.retries, exc=e)
        else:
            raise
    except Exception as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_simple_email", str(e)))
        if retry_required:
            raise self.retry(countdown=3 ** self.request.retries, exc=e)
        else:
            raise


@shared_task(
    name="task_send_template_email",
    queue="email_queue",
    bind=True,
    max_retries=3,
    soft_time_limit=10,)
def task_send_template_email(self, user_external_id: str, sender_email: str, sender_name: str,
                             to_email: str, template_id: str, dynamic_template_data: dict, retry_required: bool = True):
    try:
        EmailClientWrapper(EmailClientType.ANY).send_template_email(user_external_id, sender_email, sender_name,
                                                                    to_email, template_id, dynamic_template_data)
    except SoftTimeLimitExceeded as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_template_email", str(e)))
        if retry_required:
            raise self.retry(countdown=3 ** self.request.retries, exc=e)
        else:
            raise
    except Exception as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_template_email", str(e)))
        if retry_required:
            raise self.retry(countdown=3 ** self.request.retries, exc=e)
        else:
            raise
