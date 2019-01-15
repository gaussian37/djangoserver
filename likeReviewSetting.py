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
# RestaurantViewSet Import
from dining.views import RestaurantViewSet

# RestaurantViewSet 객체 생성
rv = RestaurantViewSet()
# like, review 테이블을 prefetch_related로 모든 객체 불러옵니다.
qs = Restaurant.objects.all().prefetch_related("like_set", "review_set")

# likeNum과 reviewNum 갱신합니다.
for q in qs:    
    rv.saveLikeReviewNum(q)


# 현재 시간 프린트
now = time.localtime()
s = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
sys.stdout = open("/home/gaussian37/djangoserver/likeReviewSettingTime.txt", "a")
print(s)
