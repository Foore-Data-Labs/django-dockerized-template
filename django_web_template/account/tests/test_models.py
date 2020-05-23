from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import PlatformUser


class PlatformUserTestCases(TestCase):
    """ Tests for PlatformUser model """

    def test_create_platform_user_simple(self):
        password = "password"
        phone = "phone"
        user = PlatformUser.objects.create_user(phone=phone, password=password)
        self.assertEqual(user.get_phone(), phone)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_admin, False)
        self.assertEqual(PlatformUser.objects.get(
            phone=phone).pk, user.get_user_id())

    def test_create_platform_user_no_phone(self):
        password = "password"
        phone = None
        with self.assertRaises(ValueError):
            user = PlatformUser.objects.create_user(
                phone=phone, password=password)

    def test_create_platform_user_no_password(self):
        phone = "phone"
        user = PlatformUser.objects.create_user(phone=phone)
        self.assertEqual(user.get_phone(), phone)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_admin, False)

    def test_create_platform_user_duplicate_phone(self):
        phone = "phone-1"
        user = PlatformUser.objects.create_user(phone=phone)
        self.assertEqual(user.get_phone(), phone)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_admin, False)

        with self.assertRaises(IntegrityError):
            user = PlatformUser.objects.create_user(phone=phone)

    def test_create_platform_user_simple_name(self):
        password = "password"
        phone = "phone"
        name = "name"
        user = PlatformUser.objects.create_user(phone=phone, password=password)
        self.assertEqual(user.get_phone(), phone)
        user.set_name(name, True)
        self.assertEqual(user.get_name(), name)
