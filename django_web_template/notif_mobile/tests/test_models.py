import time
import uuid
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from ..models import MobileFcm, BaseNotifcation

from common.constants import PlatformUserType,  FcmTokentype, FcmResult

PlatformUser = get_user_model()


class BaseNotifcationTestCases(TestCase):
    """ Tests for MobileFcm model """

    def test_create_simple_sms(self):
        user_external_id = str(uuid.uuid4())
        status = FcmResult.SENT
        token_type = FcmTokentype.ANDROID
        content = {
            'title': "title"
        }
        base_notification = BaseNotifcation.create(
            content, token_type, status, user_external_id)
        self.assertEqual(base_notification.token_type, token_type.value)
        self.assertEqual(base_notification.content, content)

        self.assertEqual(
            str(base_notification.user_external_id), user_external_id)
        self.assertEqual(base_notification.status, status.value)
        self.assertEqual(str(base_notification),
                         f"{user_external_id} - {status.value}")


class MobileFcmTestCases(TestCase):
    """ Tests for MobileFcm model """

    def setUp(self):
        password = "password"
        phone = "phone"
        self.user = PlatformUser.objects.create_user(
            phone=phone, password=password)

    def test_create_fcm_token(self):
        registration_id = "registration_id"
        user_type = PlatformUserType.AGENT
        token_type = FcmTokentype.WEB
        fcm_token = MobileFcm.create_token(
            self.user, user_type, registration_id, token_type)
        self.assertEqual(fcm_token.platform_user, self.user)
        self.assertEqual(fcm_token.platform_user_type, user_type)
        self.assertEqual(fcm_token.registration_id, registration_id)
        self.assertEqual(fcm_token.token_type, token_type.value)
        self.assertEqual(str(fcm_token), self.user.phone +
                         " - "+registration_id)

    def test_get_devices(self):
        registration_id = "registration_id"
        registration_id_2 = "registration_id_2"
        user_type = PlatformUserType.AGENT
        token_type = FcmTokentype.WEB
        fcm_token = MobileFcm.create_token(
            self.user, user_type, registration_id, token_type)
        fcm_token_2 = MobileFcm.create_token(
            self.user, user_type, registration_id_2, token_type)
        registration_ids = [
            token.registration_id for token in MobileFcm.get_devices_for_user(self.user, user_type)]
        self.assertEqual(registration_id in registration_ids, True)
        self.assertEqual(registration_id_2 in registration_ids, True)
        self.assertEqual(len(registration_ids), 2)

    def test_get_devices_without_usertype(self):
        registration_id = "registration_id"
        registration_id_2 = "registration_id_2"
        token_type = FcmTokentype.ANDROID
        user_type = PlatformUserType.AGENT
        fcm_token = MobileFcm.create_token(
            self.user, user_type, registration_id, token_type)
        fcm_token_2 = MobileFcm.create_token(
            self.user, user_type, registration_id_2, token_type)
        registration_ids = [
            token.registration_id for token in MobileFcm.get_devices_for_user(self.user)]
        self.assertEqual(registration_id in registration_ids, True)
        self.assertEqual(registration_id_2 in registration_ids, True)
        self.assertEqual(len(registration_ids), 2)

    def test_get_devices_invalid_type(self):
        with self.assertRaises(AttributeError):
            MobileFcm.get_devices_for_user(self.user, 100)

    def test_send_display_message(self):
        registration_id = "registration_id"
        user_type = PlatformUserType.AGENT
        token_type = FcmTokentype.WEB
        fcm_token = MobileFcm.create_token(
            self.user, user_type, registration_id, token_type)
        # no exception is enough for testing
        fcm_token.send_display_message("title", "body")

    def test_send_send_data_message(self):
        registration_id = "registration_id"
        user_type = PlatformUserType.AGENT
        token_type = FcmTokentype.WEB
        fcm_token = MobileFcm.create_token(
            self.user, user_type, registration_id, token_type)
        # no exception is enough for testing
        fcm_token.send_data_message({"message": "a message"})
