
from django.conf.urls import url
from jwt_auth.api import views

app_name = 'jwt_auth'

urlpatterns = [
    # POST=Signup, GET=Get info, PATCH=Update info
    url(r'^user/', views.UserView.as_view(), name='user-handler'),
    # GET=Get token, #POST=verify token
    url(r'^token/', views.TokenView.as_view(), name='token-handler'),
]
