import json
import uuid
from django.test import TestCase
from ..models import PlatformUser
from ..serializers import PlatformUserSerializer


class PlatformUserSerializerTestCases(TestCase):
    """ Tests for PlatformUserSerializer """

    def test_simple(self):
        password = "password"
        phone = "phone"
        name = "name"
        user = PlatformUser.objects.create_user(phone=phone, password=password)
        user.set_name(name, True)

        serialized_user = PlatformUserSerializer(user).data

        self.assertEqual(serialized_user['name'], name)
        self.assertEqual(serialized_user['phone'], phone)
        self.assertEqual(serialized_user['is_active'], True)
