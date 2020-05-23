import json
import time
import uuid

from typing import Tuple

from urllib.request import (Request, urlopen)
from urllib.parse import urlencode, quote_plus


from abc import ABC, abstractmethod

from django.conf import settings

from common.constants import SmsClientType, SmsResult
from common.logger import log_level_info, log_info, log_exception, log_debug_info
from .models import BaseSMS
from common import phonenumber


class _ExternalSmsWrapper(ABC):
    '''
    All SMS wrapper must implement this
    '''

    @abstractmethod
    def get_type(self) -> SmsClientType:  # pragma: no cover
        ...

    @abstractmethod
    def update_report(self, cb_data: dict):  # pragma: no cover
        ...

    @abstractmethod
    def send_sms(self, user_external_id: str, mob_num: str, sms_mess: str, sender_id: str, is_transactional: bool) -> Tuple[SmsResult, str]:  # pragma: no cover
        '''
        Returns created SMS object's status
        '''
        ...


class _DebugSmsWrapper(_ExternalSmsWrapper):
    '''
    Debug Wrapper that prints SMS to console
    '''

    def get_type(self) -> SmsClientType:
        log_info(__name__, "get_type", ">>")
        return SmsClientType.DEBUG

    def update_report(self, cb_data):  # pragma: no cover
        log_info(__name__, "update_report", ">>")

    def send_sms(self, user_external_id: str, mob_num, sms_mess, sender_id, is_transactional) -> Tuple[SmsResult, str]:
        log_info(__name__, "send_sms", ">>")
        is_valid_indian, _, indian_national_number = phonenumber.is_valid_indian_number(
            mob_num)
        if is_valid_indian:
            mob_num = str(indian_national_number)
        else:
            raise Exception("Invalid number " + str(mob_num))
        log_info(__name__, "send_sms",
                 f"mob_num-{mob_num}\nsms_mess-{sms_mess}\nsender_id-{sender_id}\nis_transactional{is_transactional}")
        external_id = str(uuid.uuid4())
        time.sleep(2)
        sms = BaseSMS.create(
            user_external_id=user_external_id,
            phone=mob_num, sms_text=sms_mess,
            client_type=self.get_type(), status=SmsResult.SENT,
            external_id=str(external_id))

        return SmsResult.SENT, external_id


class _Msg91Wrapper(_ExternalSmsWrapper):

    URL = "http://api.msg91.com/api/sendhttp.php"  # API URL

    ROUTE_PROMO: str = "1"
    ROUTE_TRANSACT: str = "4"
    SENDER_PROMO: str = "001088"
    SENDER_TRANSACT_DEFAULT: str = "SENDRID"

    RESULT_STATUS: str = 'status'
    RESULT_DELIVERY_CODE: str = 'delivery_code'

    def get_type(self) -> SmsClientType:
        return SmsClientType.MSG91

    def _convert_from_msg91(self, msg_91_status: int) -> SmsResult:
        """
            Report for MSG91SMSReport
                Codes from MSG91
                1 - Delivered
                2 - Failed
                9 - NDNC (In case of Promotional SMS only)
                16 and 25 - Rejected
                17 - Blocked number
        """
        status = SmsResult.SENT
        if msg_91_status == 1:
            status = SmsResult.DELIVERED
        elif msg_91_status == 2:
            status = SmsResult.FAILED
        elif msg_91_status == 9:  # NDNC
            status = SmsResult.FAILED
        elif msg_91_status == 16:  # REJECTED
            status = SmsResult.FAILED
        elif msg_91_status == 25:  # REJECTED
            status = SmsResult.FAILED
        elif msg_91_status == 17:  # BLOCKED
            status = SmsResult.FAILED
        return status

    def update_report(self, cb_data: dict):
        """
            {
                'data': '[
                    {
                        "senderId":"SENDRID",
                        "requestId":"386273757a69363337323739",
                        "report":[
                            {
                                "date":"2018-02-19 21:26:11",
                                "number":"917829862689",
                                "status":"1",
                                "desc":"DELIVERED"
                            }],
                        "userId":"168816",
                        "campaignName":"API"
                    }
                    ]'
            }

            ({
                'data': '[
                    {
                        "senderId":"SENDRID",
                        "requestId":"3863686a5a70303035363635",
                        "report":[
                            {
                                "date":"2018-03-08 10:53:49","number":"919900260756","status":"1","desc":"DELIVERED"
                            }],
                        "userId":"168816","campaignName":"API"
                    },
                    {
                        "senderId":"SENDRID",
                        "requestId":"3863686a5a6d333036373738",
                        "report":[
                            {
                                "date":"2018-03-08 10:53:47","number":"919845672578","status":"1","desc":"DELIVERED"
                            }],
                        "userId":"168816",
                        "campaignName":"API"
                    },
                    {
                        "senderId":"SENDRID",
                        "requestId":"3863686a5a6e393736393032",
                        "report":[
                            {
                                "date":"2018-03-08 10:53:47","number":"919945511755","status":"1","desc":"DELIVERED"
                            }],
                        "userId":"168816","campaignName":"API"
                    }]'}, 'MSG91')
        """

        log_level_info(1, __name__, "_update_report_for_msg91", ">>")
        data = cb_data.get('data', None)
        cb_data_json = json.loads(data)
        if cb_data_json:
            for data_content in cb_data_json:
                request_id = str(data_content['requestId'])
                report_status = int(((data_content['report'])[0])['status'])
                report_status = self._convert_from_msg91(report_status)
                # TBD:
                # Do we need this to throw exception?
                # Then we need to get instead of filter
                log_level_info(1,
                               __name__,
                               "_update_report_for_msg91",
                               "{0}--{1}".format(str(request_id), str(report_status)))
                filter_result = BaseSMS.objects.filter(
                    external_id=request_id).update(status=report_status)

                log_info(__name__, "_update_report_for_msg91",
                         "Filter result - {0}".format(str(filter_result)))
        log_level_info(1, __name__, "_update_report_for_msg91", "<<")

    def send_sms(self, user_external_id: str, mob_num: str, sms_mess: str, sender_id: str = None, is_transactional: bool = True) -> Tuple[SmsResult, str]:
        route = self.ROUTE_TRANSACT
        if sender_id is None:
            sender_id = self.SENDER_TRANSACT_DEFAULT
        if not is_transactional:
            route = self.ROUTE_PROMO
            sender_id = self.SENDER_PROMO
        is_valid_indian, _, indian_national_number = phonenumber.is_valid_indian_number(
            mob_num)
        if is_valid_indian:
            mob_num = str(indian_national_number)
        else:
            raise Exception("Invalid number " + str(mob_num))

        values = {
            'authkey': settings.MSG91_AUTH_KEY,
            'mobiles': mob_num,
            'message': quote_plus(sms_mess),
            'sender': sender_id,
            'route': route
        }
        try:

            # https://help.msg91.com/article/59-problem-with-plus-sign-api-send-sms
            data = urlencode(values).encode('utf-8')  # data should be bytes

            req = Request(self.URL, data)
            response = urlopen(req)
            result = {
                self.RESULT_STATUS: response.status
            }
            result[self.RESULT_DELIVERY_CODE] = (
                response.readline()).decode(encoding="utf-8")
            response.close()

            if not result[self.RESULT_DELIVERY_CODE]:
                raise Exception('SMS sendig Failed')

            external_id = result[self.RESULT_DELIVERY_CODE]
            status = SmsResult.SENT
            sms = BaseSMS.create(
                user_external_id=user_external_id,
                phone=mob_num, sms_text=sms_mess,
                client_type=self.get_type(), status=status,
                external_id=external_id)
            return sms.status, external_id
        except Exception as e:
            log_exception(e)
            raise


class SmsClientWrapper:
    SENDER_TRANSACT_DEFAULT = "SENDRID"

    def __init__(self, client_type: SmsClientType):

        self._handler: _ExternalSmsWrapper

        if settings.SMS_TO_CONSOLE:
            self._handler = _DebugSmsWrapper()
        elif client_type == SmsClientType.ANY:
            # For now, we always send MS91
            # in future if we are asked to picked, we can do so intelligently
            self._handler = _Msg91Wrapper()
        elif client_type == SmsClientType.MSG91:
            self._handler = _Msg91Wrapper()
        elif client_type == SmsClientType.DEBUG:
            self._handler = _DebugSmsWrapper()
        else:
            raise NotImplementedError()

    def get_client_type(self) -> SmsClientType:
        return self._handler.get_type()

    def handle_report_data(self, cb_data: dict):
        return self._handler.update_report(cb_data)

    def send_sms(self, user_external_id: str, mob_num: str, sms_mess: str, sender_id: str = None, is_transactional: bool = True) -> Tuple[SmsResult, str]:
        return self._handler.send_sms(user_external_id, mob_num, sms_mess, sender_id or self.SENDER_TRANSACT_DEFAULT, is_transactional)
