'''
Task dispatcher will be used by other Apps to communicate and enqueue SMS sending
'''
from typing import List
from .tasks import task_send_display_fcm, task_send_data_fcm
from common.logger import log_info
from common.constants import SmsClientType, PlatformUserType


def dispatch_display_notification(platform_users: List, message_title: str, message_body: str,
                                  # Note: We are wrongly using class as type while type is int. I really dont want to use enum
                                  user_type: PlatformUserType = None
                                  ):
    '''
    Send Promotional/Platform handled notification
    eg. New Offer
    '''
    for platform_user in platform_users:
        task_send_display_fcm.delay(
            message_title, message_body, platform_user.pk, user_type)


def dispatch_display_notification_to_merchant(platform_users: List, message_title: str, message_body: str):
    '''
    Send Promotional/Platform handled notification
    eg. New Offer
    '''
    log_info(__name__, "dispatch_display_notification_to_merchant", ">>")
    dispatch_display_notification(
        platform_users, message_title, message_body, PlatformUserType.MERCHANT)


def dispatch_display_notification_to_customer(platform_users: List, message_title: str, message_body: str):
    '''
    Send Promotional/Platform handled notification
    eg. New Offer
    '''
    log_info(__name__, "dispatch_display_notification_to_customer", ">>")
    dispatch_display_notification(
        platform_users, message_title, message_body, PlatformUserType.CUSTOMER)


def dispatch_display_notification_to_deliveryagent(platform_users: List, message_title: str, message_body: str):
    '''
    Send Promotional/Platform handled notification
    eg. New Offer
    '''
    log_info(__name__, "dispatch_display_notification_to_deliveryagent", ">>")
    dispatch_display_notification(
        platform_users, message_title, message_body, PlatformUserType.AGENT)


def dispatch_data_notification(platform_users: List, data_message: dict,
                               # Note: We are wrongly using class as type while type is int. I really dont want to use enum
                               user_type: PlatformUserType = None
                               ):
    '''
    Send Data notification.
    eg. App resync request
    '''
    for platform_user in platform_users:
        task_send_data_fcm.delay(data_message, platform_user.pk, user_type)


def dispatch_data_notification_to_merchant(platform_users: List, data_message: dict):
    '''
    Send Data notification to merchat app.
    eg. App resync request
    '''
    log_info(__name__, "dispatch_data_notification_to_merchant", ">>")
    dispatch_data_notification(
        platform_users, data_message, PlatformUserType.MERCHANT)


def dispatch_data_notification_to_customer(platform_users: List, data_message: dict):
    '''
    Send Data notification to customer app.
    eg. App resync request
    '''
    log_info(__name__, "dispatch_data_notification_to_customer", ">>")
    dispatch_data_notification(
        platform_users, data_message, PlatformUserType.CUSTOMER)


def dispatch_data_notification_to_deliveryagent(platform_users: List, data_message: dict):
    '''
    Send Data notification to delivery agent.
    eg. App resync request
    '''
    log_info(__name__, "dispatch_display_notification_to_deliveryagent", ">>")
    dispatch_data_notification(
        platform_users, data_message, PlatformUserType.AGENT)
