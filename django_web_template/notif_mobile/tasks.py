
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned

from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from .models import MobileFcm, BaseNotifcation
from common.constants import FcmResult, PlatformUserType


logger = get_task_logger(__name__)

PlatformUser = get_user_model()


@shared_task(
    bind=True,
    max_retries=3,
    name="task_send_display_fcm",
    queue="fcm_notification",
    soft_time_limit=20)
def task_send_display_fcm(self, message_title: str, message_body: str, user_id: int, user_type: PlatformUserType = None):
    '''
    Display messages are handled by Platform
    '''
    logger.info("{0}-{1}-{2}".format(__name__,
                                     "task_send_display_fcm", ">>"))
    try:
        platform_user = PlatformUser.objects.get(pk=user_id)
        # Note: The validity of user_type and user was done at time of adding token
        devices = MobileFcm.get_devices_for_user(platform_user, user_type)
        # TODO: Branch loop to another 1 task per device
        for device in devices:
            result = device.send_display_message(message_title, message_body)
            BaseNotifcation.create(
                {"title": message_title, 'body': message_body}, device.token_type,
                FcmResult.SENT if (
                    result and (result['success'] == 1)) else FcmResult.FAILED,
                platform_user.get_user_external_id())

    except PlatformUser.DoesNotExist as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_display_fcm", str(e)))
        return  # No retry
    except MultipleObjectsReturned as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_display_fcm", str(e)))
        # TODO: Capture via new-relic etc as this is big issue
        return  # No retry
    except SoftTimeLimitExceeded as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_display_fcm", str(e)))
        raise self.retry(countdown=2 ** self.request.retries, exc=e)
    except Exception as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_display_fcm", str(e)))
        raise self.retry(countdown=2 ** self.request.retries, exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    name="task_send_data_fcm",
    queue="fcm_notification",
    soft_time_limit=2)
def task_send_data_fcm(self, data_message: dict, user_id: int, user_type: PlatformUserType = None):
    '''
    Data messages are handled by App
    '''
    logger.info("{0}-{1}-{2}".format(__name__,
                                     "task_send_data_fcm", ">>"))
    try:
        platform_user = PlatformUser.objects.get(pk=user_id)
        # Note: The validity of user_type and user was done at time of adding token
        devices = MobileFcm.get_devices_for_user(platform_user, user_type)
        # TODO: Branch loop to another 1 task per device
        for device in devices:
            result = device.send_data_message(data_message)
            BaseNotifcation.create(
                data_message, device.token_type,
                FcmResult.SENT if (
                    result and (result['success'] == 1)) else FcmResult.FAILED,
                platform_user.get_user_external_id())
    except PlatformUser.DoesNotExist as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_data_fcm", str(e)))
        return  # No retry
    except MultipleObjectsReturned as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_data_fcm", str(e)))
        # TODO: Capture via new-relic etc as this is big issue
        return  # No retry
    except SoftTimeLimitExceeded as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_data_fcm", str(e)))
        raise self.retry(countdown=2 ** self.request.retries, exc=e)
    except Exception as e:
        logger.error("{0}-{1}-{2}".format(__name__,
                                          "task_send_data_fcm", str(e)))
        raise self.retry(countdown=2 ** self.request.retries, exc=e)
