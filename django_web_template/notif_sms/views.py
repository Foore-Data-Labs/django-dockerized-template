from .task_dispatcher import dispatch_sms_delivery_cb_for_msg91
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from common.logger import log_info


@api_view(['POST', ])
@permission_classes((AllowAny,))
def task_handle_sms_delivery_cb_for_msg91(request):
    """
    Pushes the cb data to queue and returned 200
    """
    if request.method == 'POST':
        log_info(__name__, "task_handle_sms_delivery_cb", ">>")
        dispatch_sms_delivery_cb_for_msg91(request.data)
        return Response(status=status.HTTP_200_OK)
