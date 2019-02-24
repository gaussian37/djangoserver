import os
import django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoserver.settings') # FIXME: check path
django.setup()

# Shell Plus Model Imports
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

from PIL import Image as PIL_Image
import keras
import cv2
from keras.models import load_model
import numpy as np

# 파라미터
textSize = 20

# 미분류된 이미지만 불러옵니다.
images = Image.objects.filter(category=-1)
model = load_model('resources/MobileNet2Weights.h5')

for image in images:
    fname = 'media/' + image.image.name
    img = cv2.imread(fname)
    if img is None:
        continue
    img = img[:,:,::-1]/255.
    resizedImg = cv2.resize(img, (224, 224))
    target = np.reshape(resizedImg, (1, 224, 224, 3))
    resultVector = model.predict(target)
    resultIndex = np.argmax(resultVector)
    image.category = resultIndex
    image.save()

# # 미분류된 이미지를 분류합니다.
# for image in images:
#     fname = 'djangoserver/media/' + image.image.name
#     # 글자 인식을 해서 글자 수를 이용하여 메뉴판인지 아닌지 부터 확인 합니다.
#     text = pytesseract.image_to_string(PIL_Image.open(fname))
#
#     # 글자 수가 textSize 이상이면 메뉴판으로 분류합니다.
#     if len(text) > textSize:
#         image.category = 1
#         image.save()
#
#     else:
#         # 메뉴판이 아니라면 음식/가게 중 하나로 분류 합니다.
#         pass
