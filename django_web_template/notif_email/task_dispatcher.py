'''
Task dispatcher will be used by other Apps to communicate and enqueue Email sending
'''

from .tasks import task_send_simple_email, task_send_template_email
from common.logger import log_info


def dispatch_simple_email(user_external_id: str, sender_email: str, sender_name: str,
                          to_email: str, subject: str, plain_text_content: str, html_content: str, retry_required=True):
    '''
    Send Simple Email
    '''
    log_info(__name__, "dispatch_simple_email", ">>")
    if not user_external_id:
        raise ValueError('user_external_id')
    if not to_email:
        raise ValueError('to_email')
    if not (plain_text_content or html_content):
        raise ValueError('html_content, plain_text_content')
    task_send_simple_email.delay(user_external_id, sender_email, sender_name,
                                 to_email, subject, plain_text_content, html_content, True)


def dispatch_simple_email_to_customer(platform_customer, sender_email: str, sender_name: str,
                                      subject: str, plain_text_content: str, html_content: str, retry_required=True):
    '''
    Send Simple Email to platform Customer.
    TODO: Test after platform_customer is implemented
    '''
    log_info(__name__, "dispatch_simple_email_to_customer", ">>")
    if not platform_customer:
        raise ValueError('platform_user')
    if not (plain_text_content or html_content):
        raise ValueError('html_content, plain_text_content')
    dispatch_simple_email(platform_customer.get_user_external_id(), sender_email, sender_name,
                          platform_customer.get_email(), subject, plain_text_content, html_content)


def dispatch_template_email(user_external_id: str, sender_email: str, sender_name: str,
                            to_email: str, template_id: str, dynamic_template_data: dict, retry_required=True):
    '''
    Send Teplate based Email
    '''
    log_info(__name__, "dispatch_simple_email", ">>")
    if not user_external_id:
        raise ValueError('user_external_id')
    if not to_email:
        raise ValueError('to_email')
    if not template_id:
        raise ValueError('template_id')
    if not dynamic_template_data:
        raise ValueError('dynamic_template_data')
    task_send_template_email.delay(user_external_id, sender_email, sender_name,
                                   to_email, template_id, dynamic_template_data, True)
