
from random import randint

from django.utils import timezone

from django.db import models
from django.conf import settings

from common.datetime import (
    TIMEZONE_CODES,
    local_current_datetime_from_active_tz,
    fifteen_minutes_later)


class AuthTempCode(models.Model):
    TOKEN_LEN = 6
    """
    SMS OTP for signin.
    code={}
        Delete on use
        Delete every 5 minutes
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=16, unique=True)
    valid_till = models.DateTimeField(default=fifteen_minutes_later)

    def __str__(self):  # pragma: no cover
        return str(self.user)

    class Meta:
        unique_together = (("token", "user"),)

    @classmethod
    def create_for_user(cls, user, valid_till_provider=None):

        # Delete first.
        cls.objects.filter(user=user).delete()

        loop_count = 0
        token = str(randint(0, 10**(cls.TOKEN_LEN-1)))
        while(True):
            loop_count += 1
            if not cls.objects.filter(token=token).exists():
                break
            if loop_count > 500:  # pragma: no cover
                token = None
                break
            token = str(randint(0, 10**(cls.TOKEN_LEN-1)))  # pragma: no cover
        # make sure token length is TOKEN_LEN
        token = ("0"*(cls.TOKEN_LEN-len(token)))+token
        if not valid_till_provider:
            valid_till_provider = fifteen_minutes_later
        valid_till = valid_till_provider()
        cls(user=user, token=token, valid_till=valid_till).save()
        return token

    @classmethod
    def verify_for_token_user(cls, token, user):
        success = False
        current_dt = local_current_datetime_from_active_tz()
        query_set = cls.objects.filter(token=token, user=user)
        if not query_set.exists():
            return success
        if query_set.count() == 1 and query_set[0].valid_till > current_dt:
            success = True
        query_set.delete()
        return success
