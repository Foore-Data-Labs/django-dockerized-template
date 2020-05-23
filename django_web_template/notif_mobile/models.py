from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

from common.logger import (log_info, log_warning, )
from .external_wrapper import fcm_send_data_message, fcm_send_display_message

from common.constants import PlatformUserType
from common.constants import Length, FcmResult, FcmTokentype


class MobileFcm(models.Model):

    platform_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # When we have to send a notification to a merchant,
    # just the user cannot uniquely identify
    # When we have to send a notification to a customer, merchant etc, we will need to identify uset_type
    # sometimes we may not care, for example, password OTP, in that case, just the user is enough
    platform_user_type = models.PositiveIntegerField(
        choices=PlatformUserType.get_choices())
    # We can use platform specific params for FCM based on this.
    token_type = models.PositiveIntegerField(
        choices=FcmTokentype.get_choices())

    # https://www.postgresql.org/docs/9.0/datatype-character.html
    # There is no performance difference among these three types (Char vs Text)
    registration_id = models.TextField(
        verbose_name="Registration token", blank=False, null=False)

    def __str__(self):
        return f"{self.platform_user} - {self.registration_id}"

    @ classmethod
    def get_devices_for_user(cls, platform_user, platform_user_type: PlatformUserType = None):
        '''
        Get devices for user. Pass platform_user_type=None for no filtering on type
        '''
        all_devices = cls.objects.filter(platform_user=platform_user)
        if not platform_user_type:
            return all_devices
        return all_devices.filter(platform_user_type=platform_user_type.value)

    def send_data_message(self, data_message: dict, api_key=None):
        log_info(__name__, "send_data_message", ">>")
        result = fcm_send_data_message(
            self.registration_id,
            data_message=data_message,
            api_key=api_key)

        # TODO: Remove below behaviour if we are periodically asking for working IDs using fcm wrapper
        if 'error' in result['results'][0]:  # pragma : no cover
            if settings.NOTIF_MOBILE_DELETE_INACTIVE_DEVICES:
                self.delete()
            else:
                self.update(active=False)
        log_info(__name__, "send_data_message", "<<")
        return result

    def send_display_message(self, message_title, message_body=None, api_key=None):

        result = fcm_send_display_message(
            self.registration_id,
            message_title=message_title,
            message_body=message_body,
            api_key=api_key)

        # TODO: Remove below behaviour if we are periodically asking for working IDs using fcm wrapper
        if 'error' in result['results'][0]:  # pragma: no cover
            if settings.NOTIF_MOBILE_DELETE_INACTIVE_DEVICES:
                self.delete()
            else:
                self.update(active=False)

        return result

    @ classmethod
    def create_token(cls, platform_user, platform_user_type, registration_id: str, token_type: FcmTokentype):
        '''
        Create token. Doesn't verify that user and user_type combination exists
        '''
        fcm_token = cls(platform_user=platform_user,
                        platform_user_type=platform_user_type, registration_id=registration_id, token_type=token_type.value)
        fcm_token.save()
        return fcm_token


class BaseNotifcation(models.Model):
    '''
    Notificaiton that was sent to a device.
    '''
    # Sent to whom?
    user_external_id = models.CharField(
        max_length=Length.UUID_LEN, blank=True)

    content = JSONField(default=dict)

    token_type = models.PositiveIntegerField(
        choices=FcmTokentype.get_choices())

    status = models.PositiveIntegerField(
        default=FcmResult.SENT.value, choices=FcmResult.get_choices())

    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return f"{self.user_external_id} - {self.status}"

    @ classmethod
    def create(cls, content: dict, token_type: int = FcmTokentype.ANDROID, status: FcmResult = FcmResult.SENT,
               user_external_id: str = None  # User ID.
               ) -> 'BaseNotifcation':

        params = {
            'content': content,
            'token_type': token_type,
            'status': status.value,
        }
        if user_external_id:
            params['user_external_id'] = user_external_id

        notification = cls(**params)
        notification.save()
        return notification
