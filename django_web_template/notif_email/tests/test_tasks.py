from django_web_template import celery_app
import time
import uuid
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from ..models import BaseEmail

from common.constants import PlatformUserType,  EmailClientType, EmailResult
from ..external_wrapper import EmailClientWrapper
from ..tasks import task_send_simple_email, task_send_template_email

PlatformUser = get_user_model()


class EmailTaskTestCases(TestCase):
    """ Tests for Email Tasks """

    def setUp(self):
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_task_send_simple_email(self):
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
        task_send_simple_email.delay(user_external_id, sender_email, sender_name,
                                     to_email, subject, plain_text_content, html_content)

    def test_task_send_template_email(self):
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
        task_send_template_email.delay(user_external_id, sender_email, sender_name,
                                       to_email, str(uuid.uuid4()), {})
