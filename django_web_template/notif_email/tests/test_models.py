import time
import uuid
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from ..models import BaseEmail

from common.constants import PlatformUserType,  EmailClientType, EmailResult

PlatformUser = get_user_model()


class BaseEmailTestCases(TestCase):
    """ Tests for BaseEmail model """

    def test_create_simple_email(self):
        user_external_id = str(uuid.uuid4())
        email = "eamil@email.com"
        content: Dict[str, str] = {
            'subject': "Subject",
            'body': 'Email Body'
        }
        client_type = EmailClientType.SENDGRID
        external_id = str(uuid.uuid4())
        status = EmailResult.SENT
        base_email = BaseEmail.create(
            content, email, client_type, status, external_id, user_external_id)
        self.assertEqual(base_email.get_status(), status)
        self.assertEqual(base_email.get_content(), content)
        self.assertEqual(base_email.get_client_type(), client_type)
        self.assertEqual(str(base_email.external_id), external_id)
        self.assertEqual(str(base_email.user_external_id), user_external_id)
        self.assertEqual(
            str(base_email), f"{user_external_id} - {status.value}")

    def test_create_no_email(self):
        user_external_id = str(uuid.uuid4())
        email = None
        content: Dict[str, str] = {
            'subject': "Subject",
            'body': 'Email Body'
        }
        client_type = EmailClientType.SENDGRID
        external_id = str(uuid.uuid4())
        status = EmailResult.SENT
        with self.assertRaises(IntegrityError):
            base_email = BaseEmail.create(
                content, email, client_type, status, external_id, user_external_id)
