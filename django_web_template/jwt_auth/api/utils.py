import random
import string

from account.models import PlatformUser
from jwt_auth.settings import api_settings
from account.serializers import PlatformUserSerializer


def user_token_info(token, user):
    content = {
        "token": token,
        "user": PlatformUserSerializer(user, many=False).data,
    }
    return content


def get_login_info_for_user(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return user_token_info(token, user)


def is_phone_taken(phone):
    return PlatformUser.objects.filter(phone=phone).exists()


def create_user(phone, password):
    return PlatformUser.objects.create_user(phone=phone, password=password)
