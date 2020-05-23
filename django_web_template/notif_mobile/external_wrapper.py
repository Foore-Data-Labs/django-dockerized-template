from typing import List, Dict, Any
from django.conf import settings

# https://pypi.org/project/pyfcm/
# https://firebase.google.com/docs/cloud-messaging/concept-options#notifications_and_data_messages
# Targeting app instances on all platforms — iOS, Android, and web
from pyfcm import FCMNotification

from common.logger import (log_info, log_warning, log_debug_info)


class DebugPushService:
    def __init__(self, api_key: str):
        log_info(__name__, "__init__", ">>")
        log_info(__name__, "__init__", api_key)
        pass
    '''
    Dummy Push service for Testing
    '''
    @classmethod
    def single_device_data_message(cls, **kwargs):
        log_info(__name__, "single_device_data_message", ">>")
        log_info(__name__, "single_device_data_message", kwargs)
        return {"results": [{"sucess": True}]}
    notify_single_device = single_device_data_message
    notify_topic_subscribers = single_device_data_message

    @classmethod
    def subscribe_registration_ids_to_topic(cls, **kwargs):
        log_info(__name__, "subscribe_registration_ids_to_topic", ">>")
        log_info(__name__, "subscribe_registration_ids_to_topic", kwargs)
        return True
    unsubscribe_registration_ids_to_topic = subscribe_registration_ids_to_topic

    @classmethod
    def clean_registration_ids(cls, registration_ids):
        log_info(__name__, "clean_registration_ids", ">>")
        log_info(__name__, "clean_registration_ids", registration_ids)
        return registration_ids


# We could have created class to wrap Google FCM, but i don't see any other 3rd party wrapper being used
gpush_service = DebugPushService if settings.FCM_TO_CONSOLE else FCMNotification


def fcm_send_data_message(registration_id: str, data_message: dict, api_key: str = None,):
    log_debug_info("fcm", "fcm_send_data_message", ">>")
    '''
    Use data messages when you want to process the messages on your client app.

    FCM(iOS, Android, and web) sees this is as - 

    {
        "message":{
            "token":"bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1...",
            "data":{
            "Nick" : "Mario",
            "body" : "great match!",
            "Room" : "PortugalVSDenmark"
            }
        }
    }
    '''
    if api_key is None:
        api_key = settings.NOTIF_MOBILE_FCM_SERVER_KEY
    push_service = gpush_service(api_key=api_key)
    result = push_service.single_device_data_message(
        registration_id=registration_id,
        data_message=data_message)
    log_debug_info("fcm", "fcm_send_data_message", "<<")
    return result


def fcm_send_display_message(registration_id: str, message_title: str, message_body: str, data_message: dict = None, api_key: str = None):
    '''
    Use notification messages when you want FCM to handle displaying a notification on your client app's behalf.
    Use data messages when you want to process the messages on your client app.

    FCM can send a notification message including an optional data payload.
    In such cases, FCM handles displaying the notification payload, and the client app handles the data payload.

    FCM sees this as - 
        {
            "message":{
                "token":"bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1...",
                "notification":{
                "title":"Portugal vs. Denmark",
                "body":"great match!"
            },
            "data" : {
                "Nick" : "Mario",
                "Room" : "PortugalVSDenmark"
            }
        }
    }
    '''
    log_debug_info("fcm", "fcm_send_display_message", ">>")
    if api_key is None:
        api_key = settings.NOTIF_MOBILE_FCM_SERVER_KEY
    push_service = gpush_service(api_key=api_key)

    kwargs: Dict[str, Any] = {
        registration_id: registration_id
    }
    if message_title:
        kwargs['message_title'] = message_title
    if message_body:
        kwargs['message_body'] = message_body
    if data_message:
        kwargs['data_message'] = data_message
    result = push_service.notify_single_device(**kwargs)
    log_debug_info("fcm", "fcm_send_display_message", "<<")
    return result


def get_clean_registration_ids(registration_ids: List[str], api_key: str = None):  # pragma: no cover
    '''
    Can be used to periodically clean the stored IDs.
    '''
    log_debug_info("fcm", "get_clean_registration_ids", ">>")
    if api_key is None:
        api_key = settings.NOTIF_MOBILE_FCM_SERVER_KEY
    push_service = gpush_service(api_key=api_key)
    clean_ids = push_service.clean_registration_ids(registration_ids)
    log_debug_info("fcm", "get_clean_registration_ids", "<<")
    return clean_ids


def subscribe_registration_ids_to_topic(topic: str, registration_ids: List[str], api_key: str = None) -> bool:  # pragma: no cover
    log_debug_info("fcm", "subscribe_registration_ids_to_topic", ">>")
    if api_key is None:
        api_key = settings.NOTIF_MOBILE_FCM_SERVER_KEY
    push_service = gpush_service(api_key=api_key)
    subscribed = push_service.subscribe_registration_ids_to_topic(
        registration_ids, topic)
    log_debug_info("fcm", "subscribe_registration_ids_to_topic", "<<")
    return subscribed


def unsubscribe_registration_ids_to_topic(topic: str, registration_ids: List[str], api_key: str = None) -> bool:  # pragma: no cover
    log_debug_info("fcm", "unsubscribe_registration_ids_to_topic", ">>")
    if api_key is None:
        api_key = settings.NOTIF_MOBILE_FCM_SERVER_KEY
    push_service = gpush_service(api_key=api_key)
    unsubscribed = push_service.unsubscribe_registration_ids_to_topic(
        registration_ids, topic)
    log_debug_info("fcm", "unsubscribe_registration_ids_to_topic", "<<")
    return unsubscribed


def fcm_send_display_message_to_topic(message_body: str, topic_name: str = None, condition: str = None, api_key: str = None):  # pragma: no cover
    '''
    Send display message to either named topic or via condition

    Followig is an example of topic condition
    topic_condition = "'TopicA' in topics && ('TopicB' in topics || 'TopicC' in topics)"

    '''
    log_debug_info("fcm", "fcm_send_display_message_to_topic", ">>")
    if api_key is None:
        api_key = settings.NOTIF_MOBILE_FCM_SERVER_KEY
    push_service = gpush_service(api_key=api_key)
    kwargs: Dict[str, Any] = {
        "message_body": message_body
    }
    if topic_name:
        kwargs["topic_name"] = topic_name
    else:
        kwargs["condition"] = condition
    result = push_service.notify_topic_subscribers(**kwargs)
    log_debug_info("fcm", "fcm_send_display_message_to_topic", "<<")
    return result
