from typing import Dict, AnyStr
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings

from common.constants import Length, EmailResult, EmailClientType


class BaseEmail(models.Model):
    '''
    Email that was sent to a device.
    '''
    # Sent to whom?
    user_external_id = models.CharField(
        max_length=Length.UUID_LEN, blank=True)

    email = models.EmailField(blank=False, null=False)

    content = JSONField(default=dict)
    external_id = models.CharField(max_length=512, blank=True, null=False)

    client_type = models.PositiveIntegerField(
        choices=EmailClientType.get_choices())
    status = models.PositiveIntegerField(
        default=EmailResult.SENT.value, choices=EmailResult.get_choices())

    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return f"{self.user_external_id} - {self.status}"

    @ classmethod
    def create(cls, content: Dict, email: str, client_type: EmailClientType, status: EmailResult = EmailResult.SENT,
               external_id: str = None,  # Email Id for 3rd party client
               user_external_id: str = None  # User ID.
               ) -> 'BaseEmail':

        params = {
            'content': content,
            'email': email,
            'status': status.value,
            'client_type': client_type.value,
        }
        if user_external_id:
            params['user_external_id'] = user_external_id
        if external_id:
            params['external_id'] = external_id

        email = cls(**params)
        email.save()
        return email

    def get_client_type(self) -> EmailClientType:
        return EmailClientType(self.client_type)

    def get_status(self) -> EmailResult:
        return EmailResult(self.status)

    def get_content(self) -> Dict:
        return self.content
