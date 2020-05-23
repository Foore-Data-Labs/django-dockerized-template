from common.constants import PlatformUserType
from ..models import MobileFcm
import json
import uuid
import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from common.constants import FcmTokentype
PlatformUser = get_user_model()


class MobileFcmApis(APITestCase):
    """ Test MobileFcm token create """

    def setUp(self):
        password = "password"
        phone = "+917829862689"
        self.user = PlatformUser.objects.create_user(
            phone=phone, password=password)
        self.user_payload = {'name': None,
                             'phone': '+917829862689', 'is_active': True}

    def test_create_token(self):
        url = reverse("notif_mobile:handler-fcm-token",
                      kwargs={"user_type": "MERCHANT"})
        fcm_token = "registation-id"
        payload = {"fcm_token": fcm_token,
                   'token_type': 'WEB'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tokens = [
            token.registration_id for token in MobileFcm.get_devices_for_user(self.user)]
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], fcm_token)

    def test_create_token_duplicate(self):
        url = reverse("notif_mobile:handler-fcm-token",
                      kwargs={"user_type": "MERCHANT"})
        fcm_token = "registation-id"
        payload = {"fcm_token": fcm_token,
                   'token_type': 'ANDROID'}
        self.client.force_authenticate(user=self.user)
        self.client.post(
            url, data=json.dumps(payload), content_type='application/json')
        response = self.client.post(
            url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code,
                         status.HTTP_208_ALREADY_REPORTED)

    def test_create_token_no_payload(self):
        url = reverse("notif_mobile:handler-fcm-token",
                      kwargs={"user_type": "MERCHANT"})
        fcm_token = "registation-id"
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_type(self):
        url = reverse("notif_mobile:handler-fcm-token",
                      kwargs={"user_type": "MERCHANT"})
        fcm_token = "registation-id"
        payload = {"fcm_token": fcm_token, 'token_type': 'invalid-token-type'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
