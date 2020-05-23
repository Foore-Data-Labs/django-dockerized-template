import time
import uuid
from django.conf import settings
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from ..models import BaseEmail

from common.constants import PlatformUserType,  EmailClientType, EmailResult
from ..external_wrapper import EmailClientWrapper

PlatformUser = get_user_model()


class DebugEmailWrapperTestCases(TestCase):
    """ Tests for DebugEmail Wrapper model """

    def test_send_email_with_debug_wrapper(self):
        client_type = EmailClientType.DEBUG
        wrapper = EmailClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        to_email = "mahori@your-org.com"
        sender_email = "mahori@your-org.com"
        sender_name = "Ravinder Mahori"
        subject = "Subject"
        plain_text_content = "Hey!"
        html_content = "<strong>Hey!</strong>"
        (result, external_id) = wrapper.send_email(user_external_id, sender_email, sender_name,
                                                   to_email, subject, plain_text_content, html_content)
        self.assertEqual(result, EmailResult.SENT)
        base_email = BaseEmail.objects.get(external_id=external_id)
        self.assertEqual(base_email.get_client_type(), client_type)
        self.assertEqual(base_email.email, to_email)
        self.assertEqual(base_email.user_external_id, user_external_id)

    def test_send_template_email_with_debug_wrapper(self):
        client_type = EmailClientType.DEBUG
        wrapper = EmailClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        to_email = "mahori@your-org.com"
        sender_email = "mahori@your-org.com"
        sender_name = "Ravinder Mahori"
        template_id = "template-id"
        dynamic_template_data = {'subject': "Email-Subject"}
        (result, external_id) = wrapper.send_template_email(
            user_external_id, sender_email, sender_name,
            to_email, template_id, dynamic_template_data)
        self.assertEqual(result, EmailResult.SENT)
        base_email = BaseEmail.objects.get(external_id=external_id)
        self.assertEqual(base_email.get_client_type(), client_type)
        self.assertEqual(base_email.email, to_email)
        self.assertEqual(base_email.user_external_id, user_external_id)

    def test_send_email_with_no_email(self):
        client_type = EmailClientType.DEBUG
        wrapper = EmailClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        to_email = None
        sender_email = "mahori@your-org.com"
        sender_name = "Ravinder Mahori"
        subject = "Subject"
        plain_text_content = "Hey!"
        html_content = "<strong>Hey!</strong>"
        with self.assertRaises(ValueError):
            wrapper.send_email(user_external_id, sender_email, sender_name,
                               to_email, subject, plain_text_content, html_content)


class SendgridEmailWrapperTestCases(TestCase):
    """ Tests for Sendgrid Wrapper.
    Requires setting EMAIL_TO_CONSOLE false explcitly in settings
    """

    def test_send_email_with_sendgrid_wrapper(self):
        if settings.EMAIL_TO_CONSOLE: return
        client_type = EmailClientType.SENDGRID
        wrapper = EmailClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        to_email = "mahori@your-org.com"
        sender_email = "mahori@your-org.com"
        sender_name = "Ravinder Mahori"
        subject = "Subject"
        plain_text_content = "Hey!"
        html_content = "<strong>Hey!</strong>"
        (result, external_id) = wrapper.send_email(user_external_id, sender_email, sender_name,
                                                   to_email, subject, plain_text_content, html_content)
        self.assertEqual(result, EmailResult.SENT)
        base_email = BaseEmail.objects.get(external_id=external_id)
        self.assertEqual(base_email.get_client_type(), client_type)
        self.assertEqual(base_email.email, to_email)
        self.assertEqual(base_email.user_external_id, user_external_id)
