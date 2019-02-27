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

# 학습된 모델을 불러 옵니다.
model = load_model('/home/bluemen/djangoserver/resources/MobileNet2Weights.h5')
baseUrl = "http://bluemen.pythonanywhere.com"


while(1):
    # 미분류된 이미지만 불러옵니다.
    images = Image.objects.filter(category=-1).select_related("restaurant")

    # 미분류된 이미지를 순회하면서 이미지 분류 처리를 합니다.
    # 만약 식당의 대표이미지가 없다면 첫 등록된 음식 이미지를 식당 대표이미지로 지정합니다.
    for image in images:
        # 저장된 이미의 경로를 가져옵니다.
        fname = 'media/' + image.image.name
        # opencv로 이미지를 읽어 옵니다.
        img = cv2.imread(fname)
        # 만약 img가 불러오지 못한다면 무시합니다.
        if img is None:
            continue
        # 학습할 때 적용된 normalize 처리와 BGR을 RGB 타입으로 바꾸어 줍니다.
        img = img[:,:,::-1]/255.
        # 학습된 사이즈에 맞게 이미지를 resize 해줍니다.
        resizedImg = cv2.resize(img, (224, 224))
        # 학습된 shape에 맞게 reshape을 해줍니다.
        target = np.reshape(resizedImg, (1, 224, 224, 3))
        # 학습된 모델에 입력하여 분류를 합니다.
        resultVector = model.predict(target)
        # 결과 벡터에서 가장 큰값의 index를 받아 옵니다.
        resultIndex = np.argmax(resultVector)
        # index를 category에 저장합니다.
        image.category = resultIndex
        # 작업한 내용을 db에 저장합니다.
        image.save()

        # 분류한 이미지가 음식(0)이고 식당의 대표이미지가 없다면 대표이미지로 설정합니다.
        restaurantInstance = image.restaurant
        if resultIndex==0 and restaurantInstance.representativeImage == '' :
            print("!!")
            restaurantInstance.representativeImage = baseUrl + image.image.url
            # 작업한 내용을 db에 저장합니다.
            restaurantInstance.save()        


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
