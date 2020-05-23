import random
from datetime import timedelta

from django_web_template.settings import DEBUG
from django.core.exceptions import MultipleObjectsReturned

from jwt_auth.settings import api_settings

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from common.logger import (
    log_error, log_warning, log_info, log_exception)
from jwt_auth.models import AuthTempCode

from common.permissions import ActivePermission
from common import phonenumber

from .utils import user_token_info, create_user, is_phone_taken, PlatformUserSerializer, PlatformUser
from jwt_auth.api.utils import get_login_info_for_user


def _create_new_user(phone):
    parsed_e164 = None
    if phone:
        is_valid_number, parsed_e164, _, _ = phonenumber.validate_and_return_param(
            phone)
        if not is_valid_number:
            content = {'message': 'Phone number invalid', 'phone': phone}
            return None, content
        if is_phone_taken(parsed_e164):
            content = {
                'message': 'Account exists for this phone, try login instead.', 'phone': parsed_e164}
            return None, content

        user = create_user(parsed_e164, None)
        if user:
            # dispatch_user_created(user)
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # Note: We are passing expiration delta explicitly here
            # Though right now, it is same as default value, in future, we
            # may send a shortly expiring token in begining and let user
            # get a long duration token in subsequent logins
            payload = jwt_payload_handler(
                user, expiration_delta=api_settings.JWT_INITIAL_EXPIRATION_DELTA)
            token = jwt_encode_handler(payload)
            return user, user_token_info(token, user)

    content = {'message': 'Paramters missing'}
    return None, content


class UserView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, format=None):  # Get User info
        log_info(__name__, "get", ">>")
        self.permission_classes = (IsAuthenticated, ActivePermission,)
        self.perform_authentication(request)
        self.check_permissions(request)
        return Response(PlatformUserSerializer(request.user, many=False).data, status=status.HTTP_200_OK)

    def post(self, request, format=None):  # Signup
        log_info(__name__, "post", ">>")
        self.permission_classes = (AllowAny,)
        phone = request.data.get("phone", None)
        user, content = _create_new_user(phone)
        response_status = status.HTTP_201_CREATED if user else status.HTTP_400_BAD_REQUEST
        return Response(content, status=response_status)

    def patch(self, request, format=None):  # Update User Info
        log_info(__name__, "patch", ">>")
        self.permission_classes = (IsAuthenticated, ActivePermission,)
        self.perform_authentication(request)
        self.check_permissions(request)
        user = request.user
        if 'name' in request.data:
            user.set_name(request.data.get('name'))
        user.save()
        return Response(PlatformUserSerializer(user, many=False).data, status=status.HTTP_200_OK)


class TokenView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, format=None):  # Get OTP
        """
        Get OTP in exchange for phone
        """
        log_info(__name__, "get", ">>")
        phone = request.query_params.get("phone", None)
        if phone:
            is_valid_number, parsed_e164, _, _ = phonenumber.validate_and_return_param(
                phone)
            if not is_valid_number:
                content = {'message': 'Phone number invalid', 'phone': phone}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = PlatformUser.objects.get(phone=parsed_e164)
            except PlatformUser.DoesNotExist:
                content = {
                    'message': 'Account does not exist. Signup instead.', 'phone': phone}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_active:
                content = {'message': 'Account is deactived.', 'phone': phone}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            token = AuthTempCode.create_for_user(user=user)
            if token:
                content = {'phone': phone}
                if DEBUG:
                    content["token"] = token
                return Response(content, status=status.HTTP_200_OK)
            content = {
                'message': 'Something went wrong. Try again later', 'phone': phone}  # pragma: no cover
            return Response(content, status=status.HTTP_400_BAD_REQUEST)  # pragma: no cover
        content = {'message': 'Phone missing'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):  # Exchange phone and OTP for JWT
        """
        Post Exchage JwtToken for otp and phone
        """

        log_info(__name__, "post", ">>")
        token = request.data.get("token", None)
        phone = request.data.get("phone", None)
        user = None
        if phone:
            is_valid_number, parsed_e164, _, _ = phonenumber.validate_and_return_param(
                phone)
            if not is_valid_number:
                content = {'message': 'Phone number invalid', 'phone': phone}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = PlatformUser.objects.get(phone=parsed_e164)
            except PlatformUser.DoesNotExist:
                content = {
                    'message': 'Account does not exist. Signup instead.', 'phone': phone}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if token and user:
            if not user.is_active:
                content = {'message': 'Account is deactived.', 'phone': phone}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            if not AuthTempCode.verify_for_token_user(token, user):
                content = {'message': 'Verification Failed'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            content = get_login_info_for_user(user)
            return Response(content, status=status.HTTP_200_OK)
        content = {'message': 'Paramters missing'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
