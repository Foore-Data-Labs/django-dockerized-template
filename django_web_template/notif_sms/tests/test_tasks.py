
import time
import uuid
from django.test import TestCase
from django.db.utils import IntegrityError


from django_web_template import celery_app

from ..models import BaseSMS

from common.constants import PlatformUserType,  SmsClientType, SmsResult
from ..external_wrapper import SmsClientWrapper
from ..tasks import task_send_sms, task_handle_sms_delivery_cb


class SmsTaskTestCases(TestCase):
    """ Tests for Email Tasks """

    def setUp(self):
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_task_send_sms(self):
        client_type = SmsClientType.DEBUG
        wrapper = SmsClientWrapper(client_type)
        self.assertEqual(wrapper.get_client_type(), client_type)

        user_external_id = str(uuid.uuid4())
        to_email = "mahori@your-org.com"
        mob_num = "+917829878909"
        sms_mess = "Subject"
        sender_id = "SENDER"
        task_send_sms.delay(user_external_id, mob_num,
                            sms_mess, sender_id, True, True)
