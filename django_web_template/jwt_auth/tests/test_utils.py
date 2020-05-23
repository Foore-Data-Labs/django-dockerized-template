import time
from django.test import TestCase

from ..utils import jwt_encode_handler, jwt_decode_handler

from account.models import PlatformUser


class JwtEncodeDecodeTestCases(TestCase):
    """ Tests for JWT Encode Decode utils """

    def setUp(self):
        password = "password"
        phone = "phone"
        self.user = PlatformUser.objects.create_user(
            phone=phone, password=password)

    def test_encode_decode_simple(self):
        payload = {
            "user_id":self.user.pk,
            'a': 1,
            'b': 2,
            'c': 3,
            '4': 4,
        }
        #print("payload", payload, sep=" : ")
        token = jwt_encode_handler(payload)
        #print("token", token, sep=" : ")
        decoded_payload = jwt_decode_handler(token)
        #print("decoded_payload", decoded_payload, sep=" : ")
        self.assertEqual(payload, decoded_payload)
