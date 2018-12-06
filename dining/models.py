# dining/models.py
from django.db import models
from .media_directory import *


# 식당에 대한 정보를 저장하는 테이블
class Restaurant(models.Model):
    # required fields
    restaurantName = models.CharField(max_length=20)
    foodCategory = models.CharField(max_length=20)
    station = models.CharField(max_length=20)

    ## 음식점 위치 위도/경도
    longitude = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50)

    # option fields
    phone = models.CharField(max_length=20,
                             blank=True)
    operatingHours = models.CharField(max_length=50,
                                       blank=True)
    searchNum = models.IntegerField(default=0)
    likeNum = models.IntegerField(default=0)
    reviewNum = models.IntegerField(default=0)

    # 이미지 리스트
    ## 대표 사진 1장
    representativeImage = models.ImageField(blank=True,
                                             upload_to=representative_directory_path)

    ## 음식 사진 리스트
    foodImageList = models.TextField(blank=True)

    ## 식당 사진 리스트
    restaurantImageList = models.TextField(blank=True)

    ## 메뉴 사진 리스트
    menuImageList = models.TextField(blank=True)

    class Meta:
        ordering = ('-id',)


# 식당에 대한 "좋아요" 선택 유무를 저장하는 테이블
class LikeRestaurant(models.Model):
    # required fields
    uid = models.CharField(max_length=20)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)


# 음식 이미지 테이블
class FoodImage(models.Model):
    # required fields
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    foodImage = models.ImageField(upload_to=food_directory_path)


# 식당 이미지 테이블
class RestaurantImage(models.Model):
    # required fields
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    restaurantImage = models.ImageField(upload_to=restaurant_directory_path)


# 메뉴 이미지 테이블
class MenuImage(models.Model):
    # required fields
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menuImage = models.ImageField(upload_to=menu_directory_path)