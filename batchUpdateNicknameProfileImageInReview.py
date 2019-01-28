import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoserver.settings') # FIXME: check path
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
from dining.views import ReviewViewSet

# ReviewViewSet 객체 생성
rv = ReviewViewSet()
# like, review 테이블을 prefetch_related로 모든 객체 불러옵니다.
queryset = Review.objects.all().select_related("restaurant", "uid")

# nickname과 profileImageLink를 업데이트 합니다.
rv.updateNicknameProfileImageLink(queryset)