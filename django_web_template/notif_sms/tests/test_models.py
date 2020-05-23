import time
import uuid
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from ..models import BaseSMS

from common.constants import PlatformUserType,  FcmTokentype, SmsClientType, SmsResult

PlatformUser = get_user_model()


class BaseSMSTestCases(TestCase):
    """ Tests for MobileFcm model """

    def test_create_simple_sms(self):
        user_external_id = str(uuid.uuid4())
        phone = "+91890989878"
        sms_text = "Hey there!"
        client_type = SmsClientType.MSG91
        external_id = str(uuid.uuid4())
        status = SmsResult.SENT
        base_sms = BaseSMS.create(
            phone, sms_text, client_type, status, external_id, user_external_id)
        self.assertEqual(base_sms.phone, phone)
        self.assertEqual(base_sms.sms_text, sms_text)
        self.assertEqual(base_sms.client_type, client_type.value)
        self.assertEqual(str(base_sms.external_id), external_id)
        self.assertEqual(base_sms.status, status.value)
        self.assertEqual(str(base_sms.user_external_id), user_external_id)
        self.assertEqual(base_sms.status, status.value)
        self.assertEqual(str(base_sms), f"{phone} - {status.value}")

    def test_create_no_phone(self):
        user_external_id = str(uuid.uuid4())
        phone = None
        sms_text = "Hey there!"
        client_type = SmsClientType.MSG91
        external_id = str(uuid.uuid4())
        status = SmsResult.SENT
        with self.assertRaises(IntegrityError):
            base_sms = BaseSMS.create(
                phone, sms_text, client_type, status, external_id, user_external_id)

    def test_create_no_sms(self):
        user_external_id = str(uuid.uuid4())
        phone = "+91890989878"
        sms_text = ""
        client_type = SmsClientType.MSG91
        external_id = str(uuid.uuid4())
        status = SmsResult.SENT
        with self.assertRaises(ValueError):
            base_sms = BaseSMS.create(
                phone, sms_text, client_type, status, external_id, user_external_id)

    def test_mark_sent(self):
        user_external_id = str(uuid.uuid4())
        phone = "+91890989878"
        sms_text = "Hey there!"
        client_type = SmsClientType.MSG91
        external_id = str(uuid.uuid4())
        status = SmsResult.CREATED
        base_sms = BaseSMS.create(
            phone, sms_text, client_type, status, '', user_external_id)
        base_sms.mark_sent(external_id)
        base_sms.refresh_from_db()
        self.assertEqual(str(base_sms.user_external_id), user_external_id)
        self.assertEqual(base_sms.status, SmsResult.SENT.value)
