import enum
from typing import List, Tuple


class Length:
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    UUID_LEN = 36
    PHONE_NUMBER = 14
    PERSON_NAME = 64
    SMS_LEN_MAX = 512


class BaseIntEnum(enum.IntEnum):
    @classmethod
    def tokentype_from_string(cls, token_type: str):
        '''
        Override if call caps standard names won't work
        '''
        return cls.__members__[token_type]

    @classmethod
    def get_string_for_type(cls, token_type: 'FcmTokentype'):
        '''
        Override if call caps standard names won't work
        '''
        return token_type.name

    @classmethod
    def get_choices(cls) -> List[Tuple]:
        '''
        To be used as choices field in model definition
        '''
        return [(member.value, member.name) for member in cls]


class PlatformUserType(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    MERCHANT = 1
    CUSTOMER = 2
    AGENT = 3
    PROVIDER = 4


class SmsClientType(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    MSG91 = 1
    TWILIO = 2
    DEBUG = 99
    ANY = 100


class SmsResult(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    CREATED = 1
    SENT = 2
    DELIVERED = 3
    FAILED = 4


class EmailClientType(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    SENDGRID = 1
    DEBUG = 99
    ANY = 100


class EmailResult(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    SENT = 1
    FAILED = 2


class FcmTokentype(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    ANDROID = 1
    IOS = 2
    WEB = 3


class FcmResult(BaseIntEnum):
    '''
    Changing constants may require DB migrations. Think before changing.
    '''
    SENT = 1
    FAILED = 2
