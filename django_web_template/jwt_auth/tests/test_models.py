import time
from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import AuthTempCode
from account.models import PlatformUser

from common.datetime import (
    local_current_datetime_from_active_tz,
    fifteen_minutes_later)


class AuthTempCodeTestCases(TestCase):
    """ Tests for AuthTempCode model """

    def setUp(self):
        password = "password"
        phone = "phone"
        self.user = PlatformUser.objects.create_user(
            phone=phone, password=password)

    def test_create_otp_simple(self):
        otp = AuthTempCode.create_for_user(self.user)
        verification_result = AuthTempCode.verify_for_token_user(otp, self.user)
        self.assertEqual(verification_result, True)
        self.assertEqual(len(otp), AuthTempCode.TOKEN_LEN)

    def test_create_otp_multiple_verification_fails(self):
        otp = AuthTempCode.create_for_user(self.user)
        verification_result = AuthTempCode.verify_for_token_user(otp, self.user)
        self.assertEqual(verification_result, True)
        verification_result = AuthTempCode.verify_for_token_user(otp, self.user)
        self.assertEqual(verification_result, False)

    def test_create_platform_otp_timeout(self):
        otp = AuthTempCode.create_for_user(
            self.user, valid_till_provider=local_current_datetime_from_active_tz)
        time.sleep(1)#So that token is in past now
        verification_result = AuthTempCode.verify_for_token_user(otp, self.user)
        self.assertEqual(verification_result, False)
