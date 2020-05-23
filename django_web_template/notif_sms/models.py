from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from common.constants import Length, SmsClientType, SmsResult


class BaseSMS(models.Model):

    KEY_SMS_TEXT = "stxt"

    # Sent to whom?
    user_external_id = models.CharField(
        max_length=Length.UUID_LEN, blank=True)

    # To this number, who this number belonged to is decided by `user_external_id`
    phone = models.CharField(
        verbose_name='phone', max_length=Length.PHONE_NUMBER)

    sms_text = models.TextField(
        blank=False, null=False, max_length=Length.SMS_LEN_MAX)

    client_type = models.PositiveIntegerField(
        choices=SmsClientType.get_choices())

    status = models.PositiveIntegerField(
        default=SmsResult.CREATED.value, choices=SmsResult.get_choices())

    # ID of SMS to track delivery
    external_id = models.CharField(max_length=512, blank=True, null=False)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return f"{self.phone} - {self.status}"

    @classmethod
    def create(cls, phone: str, sms_text: str, client_type: SmsClientType, status: SmsResult = SmsResult.CREATED,
               external_id: str = None,  # SMS Id for 3rd party client
               user_external_id: str = None  # User ID.
               ):

        if not sms_text:
            raise ValueError(sms_text)
        params = {
            'sms_text': sms_text,
            'phone': phone,
            'client_type': client_type.value,
            'status': status.value,
        }
        if external_id:
            params['external_id'] = external_id
        if user_external_id:
            params['user_external_id'] = user_external_id

        sms = cls(**params)
        sms.save()
        return sms

    def mark_sent(self, external_id: str):
        BaseSMS.objects.filter(pk=self.pk).update(
            status=SmsResult.SENT.value, external_id=external_id)

    def get_client_type(self) -> SmsClientType:
        return SmsClientType(self.client_type)

    def get_status(self) -> SmsResult:
        return SmsResult(self.status)
