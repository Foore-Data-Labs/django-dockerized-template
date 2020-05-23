from django.urls import path
from .views import task_handle_sms_delivery_cb_for_msg91


urlpatterns = [
    path(r'^report/msg91/$', task_handle_sms_delivery_cb_for_msg91),
]
