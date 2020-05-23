###############################################################################
# Copyright 2020, your-org Private Limited  All rights reserved.
# You may use this file only in accordance with the license, terms, conditions,
# disclaimers, and limitations in the end user license agreement accompanying
# the software package with which this file was provided.
###############################################################################

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('kiop-a8b-5a/puk2-4okzlt-iradam-hcaan/', admin.site.urls),
    path('api/v1/auth/', include('jwt_auth.api.urls')),
    path('api/v1/notification/mobile/', include('notif_mobile.api.urls')),

]
