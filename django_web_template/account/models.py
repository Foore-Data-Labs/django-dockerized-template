import time
from django.db import models
from common.constants import Length
from common.uuid import unique_uuid4

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class PlatformUserManager(BaseUserManager):

    def create_user(self, phone, password=None):
        """
        Creates and saves a User with the given phone, and password.
        """
        if not phone:
            raise ValueError('Users must have a phone number ')

        user = self.model(phone=phone)

        password = password or self.make_random_password()

        user.set_password(password)
        # JWT secret
        user.auth_secret = self.make_random_password(
            length=self.model.CONST_AUTH_SECRET_LEN)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **kwargs):  # pragma: no cover
        """
        Creates and saves a superuser with the given phone, password.
        """
        user = self.create_user(
            phone, password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class PlatformUser(AbstractBaseUser):
    # Changing below constants requires running migrations
    CONST_AUTH_SECRET_LEN = 16

    # Models exposed to outside world will have unique UUID.
    # The key shared to outside world is this.
    # This does not replace the Integer primary key.
    external_id = models.UUIDField(default=unique_uuid4, unique=True)
    # TODO: Add index on phone
    phone = models.CharField(
        verbose_name='phone',
        max_length=Length.PHONE_NUMBER,
        unique=True)

    name = models.CharField(
        max_length=Length.PERSON_NAME,
        blank=True, null=False)

    auth_secret = models.CharField(
        verbose_name='secret',
        max_length=CONST_AUTH_SECRET_LEN,
        blank=False, null=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = PlatformUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):  # pragma: no cover
        return self.phone

    # TODO: Add DB name meta

    def get_user_id(self):
        return self.pk

    def get_user_external_id(self):
        return str(self.external_id)

    def get_phone(self):
        return self.phone

    def get_auth_secret(self):
        return self.auth_secret

    def get_name(self):
        return self.name

    def set_name(self, name, save=True):
        self.name = name
        if save:
            self.save()

    def has_perm(self, perm, obj=None):  # pragma: no cover
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):  # pragma: no cover
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):  # pragma: no cover
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
