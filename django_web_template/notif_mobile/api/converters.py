from common.constants import PlatformUserType


class UserTypeConverter:
    '''
    https://docs.djangoproject.com/en/3.0/topics/http/urls/#path-converters
    '''
    regex = '(merchant)|(customer)|(delivery)|(provider)'

    def to_python(self, value: str) -> PlatformUserType:
        '''
        Method, which handles converting the matched string into the type that should be passed to the view function.
        It should raise ValueError if it can’t convert the given value. A ValueError is interpreted as no match
        and as a consequence a 404 response is sent to the user unless another URL pattern matches.
        '''
        return PlatformUserType.tokentype_from_string(value.upper())

    def to_url(self, value: str) -> str:
        '''
        Method, which handles converting the Python type into a string to be used in the URL.
        '''
        return value.lower()
