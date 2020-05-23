import time
import uuid
from django.conf import settings
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from ..models import BaseSMS

from common.constants import PlatformUserType,  SmsClientType, SmsResult
from ..external_wrapper import SmsClientWrapper

PlatformUser = get_user_model()


class DebugSmsWrapperTestCases(TestCase):
    """ Tests for DebugSms Wrapper model """

    def test_send_sms_with_debug_wrapper(self):
        client_type = SmsClientType.DEBUG
        wrapper = SmsClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        mob_num = "+917829878909"
        sms_mess = "Subject"
        sender_id = "SENDER"
        (result, external_id) = wrapper.send_sms(
            user_external_id, mob_num, sms_mess, sender_id, True)
        self.assertEqual(result, SmsResult.SENT)
        base_sms = BaseSMS.objects.get(external_id=external_id)
        self.assertEqual(base_sms.get_client_type(), client_type)
        self.assertEqual(base_sms.user_external_id, user_external_id)
        self.assertEqual(base_sms.get_status(), SmsResult.SENT)


class MSG91SmsWrapperTestCases(TestCase):
    """ Tests for MSG91 Wrapper model """

    def test_send_sms_with_debug_wrapper(self):
        # Set false explicitly to run this test
        if settings.SMS_TO_CONSOLE:
            return

        client_type = SmsClientType.MSG91
        wrapper = SmsClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        mob_num = "+917829862689"
        sms_mess = "Subject"
        sender_id = "oMtter"
        (result, external_id) = wrapper.send_sms(
            user_external_id, mob_num, sms_mess, sender_id, True)
        self.assertEqual(result, SmsResult.SENT)
        base_sms = BaseSMS.objects.get(external_id=external_id)
        self.assertEqual(base_sms.get_client_type(), client_type)
        self.assertEqual(base_sms.user_external_id, user_external_id)
        self.assertEqual(base_sms.get_status(), SmsResult.SENT)
