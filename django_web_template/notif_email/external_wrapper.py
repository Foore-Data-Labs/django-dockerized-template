import json
import time
import uuid

from urllib.request import (Request, urlopen)

from abc import ABC, abstractmethod
from typing import Tuple

from django.core.mail import send_mail
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent

from common.constants import EmailClientType, EmailResult
from common.logger import log_level_info, log_info, log_exception, log_debug_info
from .models import BaseEmail
from common.email import is_valid_email


class _ExternalEmailWrapper(ABC):
    '''
    All SMS wrapper must implement this
    '''

    @abstractmethod
    def get_templates(self) -> dict:  # pragma: no cover
        '''
        returns dict of template_name and templateid
        '''
        ...

    @abstractmethod
    def get_type(self) -> EmailClientType:  # pragma: no cover
        ...

    @abstractmethod
    def update_report(self, cb_data: dict):  # pragma: no cover
        '''
        Kept for sake of completeness. At this point, we are not tracking delivery of emails
        though, sendgrid does provide webhook support
        '''
        ...

    @abstractmethod
    def send_template_email(self, user_external_id: str, sender_email: str, sender_name: str,
                            to_email: str, template_id: str, dynamic_template_data: dict) -> Tuple[EmailResult, str]:  # pragma: no cover
        '''
        Send using a template. Good for predefined content like OTP
        '''
        ...

    @abstractmethod
    def send_email(self, user_external_id: str, sender_email: str, sender_name: str,
                   to_email: str, subject: str, plain_text_content: str, html_content: str) -> Tuple[EmailResult, str]:  # pragma: no cover
        '''
        Send free form text/html email. Never good for developer. Probably decent for rapid prototyping
        '''
        ...


class _DebugEmailWrapper(_ExternalEmailWrapper):

    '''
    Debug Wrapper that prints SMS to console
    '''

    def get_templates(self) -> dict:  # pragma: no cover
        return {
            'OTP': 1
        }

    def get_type(self) -> EmailClientType:
        log_info(__name__, "get_type", ">>")
        return EmailClientType.DEBUG

    def update_report(self, cb_data: dict):  # pragma: no cover
        log_info(__name__, "update_report", ">>")
        log_info(__name__, "update_report", cb_data)

    def send_template_email(self, user_external_id: str, sender_email: str, sender_name: str,
                            to_email: str, template_id: str, dynamic_template_data: dict) -> Tuple[EmailResult, str]:
        '''
        Doesn't send. Just prints and create BaseEmail entity in DB
        '''
        log_info(__name__, "send_template_email", ">>")
        log_info(__name__, "send_template_email",
                 f"sender_email-{sender_email}\nsender_name-{sender_name}\nto_email-{to_email}      \\\
                 \ntemplate_id-{template_id}          \\\
                 dynamic_template_data-{dynamic_template_data}")
        external_id = str(uuid.uuid4())
        BaseEmail.create({
            'sender_email': sender_email,
            'sender_name': sender_name,
            'template_id': template_id,
            'dynamic_template_data': dynamic_template_data
        }, to_email, self.get_type(), EmailResult.SENT, external_id, user_external_id)
        return EmailResult.SENT, external_id

    def send_email(self, user_external_id: str, sender_email: str, sender_name: str,
                   to_email: str, subject: str, plain_text_content: str, html_content: str) -> Tuple[EmailResult, str]:
        '''
        Sends. Just prints and create BaseEmail entity in DB
        '''
        params = {
            'subject': subject,
            'from_email': sender_email,
            'recipient_list': [to_email], }
        if plain_text_content:
            params['message'] = plain_text_content
        if html_content:
            params['html_message'] = html_content
        log_debug_info(__name__, "send_email", params)
        send_mail(**params, fail_silently=False)
        external_id = str(uuid.uuid4())
        BaseEmail.create({
            'sender_email': sender_email,
            'sender_name': sender_name,
            'subject': subject,
            'plain_text_content': plain_text_content,
            'html_content': html_content}, to_email, self.get_type(), EmailResult.SENT, external_id, user_external_id)
        return EmailResult.SENT, external_id


class _SendgridWrapper(_ExternalEmailWrapper):

    def _get_sendgrid_client(self) -> SendGridAPIClient:
        return SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    def get_templates(self) -> dict:  # pragma: no cover
        return {}

    def send_email(self, user_external_id: str, sender_email: str, sender_name: str,
                   to_email: str, subject: str, plain_text_content: str, html_content: str) -> Tuple[EmailResult, str]:
        # https://github.com/sendgrid/sendgrid-python/blob/master/examples/helpers/mail_example.py#L16
        mail_params = {
            'from_email': From(sender_email, sender_name),
            'to_emails': to_email,
            'subject': Subject(subject),
        }
        if plain_text_content:
            mail_params['plain_text_content'] = PlainTextContent(
                plain_text_content)
        if html_content:
            mail_params['html_content'] = HtmlContent(html_content)
        message = Mail(**mail_params)
        response = self._get_sendgrid_client().send(message)
        if response and (response.status_code in [200, 202, 201]):
            external_id = response.headers['X-Message-Id']
            # External From, Subject etc are not Json Serializable
            mail_params['from_email'] = (sender_email, sender_name)
            mail_params['subject'] = subject
            if plain_text_content:
                mail_params['plain_text_content'] = plain_text_content
            if html_content:
                mail_params['html_content'] = html_content
            BaseEmail.create(mail_params, to_email, self.get_type(),
                             EmailResult.SENT, external_id, user_external_id)
            return EmailResult.SENT, external_id
        return EmailResult.FAILED, None

    def send_template_email(self, user_external_id: str, sender_email: str, sender_name: str,
                            to_email: str, template_id: str, dynamic_template_data: dict) -> Tuple[EmailResult, str]:
        # https://github.com/sendgrid/sendgrid-python/blob/master/use_cases/transactional_templates.md
        # Handlebar syntax is assumed to used for subject as well
        mail_params = {
            'from_email': From(sender_email, sender_name),
            'to_emails': to_email,
        }
        message = Mail(**mail_params)
        message.dynamic_template_data = dynamic_template_data
        message.template_id = template_id
        response = self._get_sendgrid_client().send(message)
        if response and (response.status_code in [200, 202, 201]):
            external_id = response.headers['X-Message-Id']
            mail_params['dynamic_template_data'] = dynamic_template_data
            mail_params['template_id'] = template_id
            BaseEmail.create(mail_params, to_email, self.get_type(),
                             EmailResult.SENT, external_id, user_external_id)
            return EmailResult.SENT, external_id
        return EmailResult.FAILED, None

    def update_report(self, cb_data):
        return super().update_report(cb_data)

    def get_type(self):
        return EmailClientType.SENDGRID


class EmailClientWrapper:
    DEFAULT_SENDER_EMAIL = "notification@your-org.com"
    DEFAULT_SENDER_NAME = "your-org"

    def __init__(self, client_type: EmailClientType):

        self._handler: _ExternalEmailWrapper

        if settings.EMAIL_TO_CONSOLE:
            self._handler = _DebugEmailWrapper()
            # For now, we always send Sendgrid
            # in future if we are asked to picked, we can do so intelligently
        elif client_type == EmailClientType.ANY:
            self._handler = _SendgridWrapper()
        elif client_type == EmailClientType.SENDGRID:
            self._handler = _SendgridWrapper()
        elif client_type == EmailClientType.DEBUG:
            self._handler = _DebugEmailWrapper()
        else:
            raise NotImplementedError()

    def get_templates(self) -> dict:  # pragma: no cover
        return self._handler.get_templates()

    def get_client_type(self) -> EmailClientType:
        return self._handler.get_type()

    def handle_report_data(self, cb_data: dict):  # pragma: no cover
        # No cover because we are not using delivery report for now
        return self._handler.update_report(cb_data)

    def send_email(self, user_external_id: str, sender_email: str, sender_name: str,
                   to_email: str, subject: str, plain_text_content: str, html_content: str) -> Tuple[EmailResult, str]:
        if not is_valid_email(to_email):
            raise ValueError(to_email)
        return self._handler.send_email(
            user_external_id,
            sender_email or self.DEFAULT_SENDER_EMAIL,
            sender_name or self.DEFAULT_SENDER_NAME,
            to_email, subject, plain_text_content, html_content)

    def send_template_email(self, user_external_id: str, sender_email: str, sender_name: str,
                            to_email: str, template_id: str, dynamic_template_data: dict) -> Tuple[EmailResult, str]:
        if not is_valid_email(to_email):
            raise ValueError(to_email)
        return self._handler.send_template_email(
            user_external_id,
            sender_email or self.DEFAULT_SENDER_EMAIL,
            sender_name or self.DEFAULT_SENDER_NAME,
            to_email, template_id, dynamic_template_data)
