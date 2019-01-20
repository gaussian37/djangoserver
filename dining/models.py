# dining/models.py
from django.db import models
from .utils import dist
from .media_directory import *

# 식당에 대한 정보를 저장하는 테이블
class Restaurant(models.Model):
    # required fields
    restaurantName = models.CharField(max_length=20)
    foodCategory = models.CharField(max_length=20)
    station = models.CharField(max_length=20)

    ## 음식점 위치 위도/경도
    longitude = models.FloatField()
    latitude = models.FloatField()

    # option fields
    phone = models.CharField(max_length=20,
                             blank=True)

    distFromStation = models.FloatField(blank=True)

    operatingHours = models.CharField(max_length=50,
                                       blank=True)

    searchNum = models.IntegerField(default=0)
    likeNum = models.IntegerField(default=0)
    reviewNum = models.IntegerField(default=0)

    # 대표 사진 1장의 URL
    representativeImage = models.TextField(blank=True)

    # class Meta:
    #     ordering = ('-id',)


# 식당에 대한 "좋아요" 선택 유무를 저장하는 테이블
class Like(models.Model):
    # required fields
    uid = models.CharField(max_length=20)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)


# 리뷰 테이블
class Review(models.Model):
    ## required field

    # restaurant에 대한 foreign key
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    # content : 사용자의 review 본문
    content = models.TextField()

    # uid : 등록한 사용자의 id
    uid = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add = True)


# 이미지 테이블
class Image(models.Model):
    ## required field

    # image : 음식/메뉴/식당 사진
    image = models.ImageField(upload_to="dining/%Y/%m/%d")

    # restaurant에 대한 foreign key
    restaurant = models.ForeignKey(Restaurant,
                                   related_name="images",
                                   on_delete=models.CASCADE)

    # restaurant에 대한 foreign key
    review = models.ForeignKey(Review,
                                   on_delete=models.CASCADE)

    # uid : 등록한 사용자 구분 목적
    uid = models.CharField(max_length=20)

    ## option field

    # category : 0이면 food, 1이면 menu, 2이면 restaurant
    category = models.IntegerField(blank=True, default=-1)

    # created_at : 등록한 시점
    created_at = models.DateTimeField(auto_now_add=True)

# User 정보 테이블
class User(models.Model):
    ## required field

    # uid : 등록한 사용자의 id, pk로 사용
    uid = models.CharField(max_length=20,
                           primary_key=True)

    # nickname : 앱에서 사용할 nickname
    nickname = models.CharField(max_length=50)

    # profileImageLink : 카카오 프로필의 이미지 링크를 저장
    profileImageLink = models.TextField()

    ## Non requred field

    # score : 각 사용자가 얻은 점수
    score = models.IntegerField(blank=True, default=0)

class Station(models.Model):
    ## required fields

    # station : 역 이름
    station = models.CharField(max_length=15)

    # longitude : 경도
    longitude = models.FloatField()

    # latitude : 위도
    latitude = models.FloatField()

    ## Non required fields
    # distFromStation : 입력 받은 GPS와 역과의 거리를 저장할 필드
    distFromStation = models.FloatField(blank=True, default=-1)



