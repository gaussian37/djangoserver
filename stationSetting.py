import os
import django
import sys
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoserver.settings')
django.setup()

# django_extensions의 shell_plus 실행 시 참조되는 전체 library 호출
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from dining.models import Image, Like, Restaurant, Review
from django.contrib.auth.models import Group, Permission, User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site
from rest_framework.authtoken.models import Token
# Shell Plus Django Imports
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When, Exists, OuterRef, Subquery
from django.utils import timezone
from django.urls import reverse

from dining.utils import *
import requests

diningBaseUrl = "http://gaussian37.pythonanywhere.com/dining/v1/"

# stationDict를 통하여 역 이름과 GPS 정보를 가져 옵니다.
for item in stationDict.items():
    data = {"station":item[0],
            "latitude":item[1][0],
            "longitude" :item[1][1]}
    requests.post(diningBaseUrl + "station/", data = data)
