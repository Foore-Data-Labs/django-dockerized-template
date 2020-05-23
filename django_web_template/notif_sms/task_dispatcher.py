'''
Task dispatcher will be used by other Apps to communicate and enqueue SMS sending
'''

from .tasks import task_send_sms, task_handle_sms_delivery_cb
from common.logger import log_info
from common.constants import SmsClientType


def dispatch_sms(user_external_id: str, phone: str, sms_text: str, transactional=True, retry_required=True):
    '''
    Send Generic SMS
    '''
    log_info(__name__, "dispatch_sms", ">>")
    if not user_external_id:
        raise ValueError('user_external_id')
    task_send_sms.delay(user_external_id, phone, sms_text, None, True, True)


def dispatch_otp(user_external_id: str, phone: str, otp: str):
    '''
    Send OTP sms
    '''
    log_info(__name__, "dispatch_otp", ">>")
    sms_text = f"Your OTP is {otp}"
    dispatch_sms(user_external_id, phone, sms_text, True, True)


def dispatch_sms_delivery_cb_for_msg91(cb_data):
    '''
    Handle callback/delivery update from MSG91 client
    '''
    task_handle_sms_delivery_cb.delay(cb_data, SmsClientType.MSG91)
