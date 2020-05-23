from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import MobileFcm

from common.logger import (log_warning, log_info, log_error, log_exception)
from common.permissions import ActivePermission


from common.constants import PlatformUserType, FcmTokentype


class FcmToken(APIView):

    permission_classes = (IsAuthenticated, ActivePermission, )

    def post(self, request, user_type: PlatformUserType, format=None):
        """
        Add a new FcmToken for user
        """

        log_info(__name__, "post", ">>")
        fcm_token = request.data.get('fcm_token', None)
        token_type = request.data.get('token_type', None)
        if fcm_token and token_type:
            try:
                token_type = FcmTokentype.tokentype_from_string(token_type)
                # TODO: Add check that user and user_type combination exist
                if not MobileFcm.objects.filter(
                        platform_user=request.user, platform_user_type=user_type, registration_id=fcm_token).exists():
                    fcm_token = MobileFcm.create_token(
                        request.user, user_type, fcm_token, token_type)
                    return Response(status=status.HTTP_201_CREATED)
                # TODO: Policy check. Are we sending meaningful status messages?
                return Response(status=status.HTTP_208_ALREADY_REPORTED)
            except KeyError as e:
                log_exception(e)
        content = {'message': 'invalid request'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
