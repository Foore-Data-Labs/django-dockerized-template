import json
import uuid
import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import PlatformUser


class OtpApis(APITestCase):
    """ Test module OTP get and exchange """
    url = reverse("jwt_auth:token-handler")

    def setUp(self):
        password = "password"
        phone = "+917829862689"
        self.user = PlatformUser.objects.create_user(
            phone=phone, password=password)
        self.user_payload = {'name': '',
                             'phone': '+917829862689', 'is_active': True, 'user_eid': self.user.get_user_external_id()}

    def test_get_otp(self):
        response = self.client.get(self.url, data={"phone": self.user.phone})
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], self.user.phone)

    def test_get_otp_invalid_phone(self):
        response = self.client.get(self.url, data={"phone": "+916787987876"})
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_otp_invalid_phone_2(self):
        response = self.client.get(self.url, data={"phone": "17987876"})
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_otp_no_phone(self):
        response = self.client.get(self.url)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_otp_inactive_user(self):
        password2 = "password2"
        phone2 = "+917889862681"
        user = PlatformUser.objects.create_user(
            phone=phone2, password=password2)
        user.is_active = False
        user.save()
        response = self.client.get(self.url, data={"phone": phone2})
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_use_otp(self):
        response = self.client.get(self.url, data={"phone": self.user.phone})
        # print(response.data)
        payload = {
            # For Debug we set token in response
            "token": response.data["token"],
            "phone": self.user.phone,
        }
        response = self.client.post(
            self.url, data=json.dumps(payload),
            content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('token' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual(response.data['user'], self.user_payload)

    def test_use_wrong_otp(self):
        response = self.client.get(self.url, data={"phone": self.user.phone})
        payload = {
            # For Debug we set token in response
            "token": response.data["token"]+"t",
            "phone": self.user.phone,
        }
        response = self.client.post(
            self.url, data=json.dumps(payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_use_wrong_phone_for_otp(self):
        response = self.client.get(self.url, data={"phone": self.user.phone})
        token = response.data["token"]  # For Debug we set token in response
        payload = {
            "token": token,
            "phone": self.user.phone+"0",
        }
        response = self.client.post(
            self.url, data=json.dumps(payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        payload = {
            "token": token,
            "phone": "+918909876767"
        }
        response = self.client.post(
            self.url, data=json.dumps(payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_use_wrong_otp_missing_params(self):
        response = self.client.post(
            self.url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserApis(APITestCase):
    """ Test module OTP get and exchange """
    url = reverse("jwt_auth:user-handler")

    def setUp(self):
        ###########################################
        # Create User
        password = "password"
        phone = "+917829862689"
        created_user = PlatformUser.objects.create_user(
            phone=phone, password=password)
        created_user.set_name("Ravinder", True)
        self.user = created_user
        self.user_payload = {'name': "Ravinder",
                             'phone': '+917829862689', 'is_active': True, 'user_eid': self.user.get_user_external_id()}

        ###########################################
        # Get JWT
        url = reverse("jwt_auth:token-handler")
        response = self.client.get(url, data={"phone": self.user.phone})
        # print(response.data)
        payload = {
            # For Debug we set token in response
            "token": response.data["token"],
            "phone": self.user.phone,
        }
        response = self.client.post(
            url, data=json.dumps(payload),
            content_type='application/json')
        self.token = response.data['token']
        # print('self.token', self.token, sep=" # ")

    def test_get_user_info_with_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT '+self.token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.user_payload)

    def test_get_user_info_with_auth_without_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_user_info(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT '+self.token)
        response = self.client.patch(self.url, data={"name": "Batman"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Batman")

        response = self.client.get(self.url)
        self.assertEqual(response.data['name'], "Batman")

    def test_user_signup(self):
        user_2_phone = "+917829099878"
        response = self.client.post(self.url, data={"phone": user_2_phone})
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT '+response.data["token"])
        response = self.client.get(self.url)
        self.assertEqual(response.data['phone'], user_2_phone)

    def test_user_signup_duplicate_fails(self):
        user_2_phone = self.user.phone
        response = self.client.post(self.url, data={"phone": user_2_phone})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_signup_invalid_phone(self):
        user_2_phone = "457898"
        response = self.client.post(self.url, data={"phone": user_2_phone})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
