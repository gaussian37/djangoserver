# accounts/urls.py

from django.conf.urls import include, url
from .views import KakaoLogin

app_name = 'accounts'

urlpatterns = [
    url(r'^rest-auth/kakao/$', KakaoLogin.as_view(), name='kakao_login'),
]