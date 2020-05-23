from django.urls import path, register_converter
from . import views, converters


app_name = 'notif_mobile'

register_converter(converters.UserTypeConverter, 'user-type')


# https://support.google.com/webmasters/answer/76329?hl=en
# TODO: dash over underscore
urlpatterns = [
    path(r'<user-type:user_type>/token/',
         views.FcmToken.as_view(), name="handler-fcm-token"),
]
