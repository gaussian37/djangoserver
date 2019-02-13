# dining/serializers.py

from rest_framework import serializers
from .models import Restaurant, Like, Image, Review, Users, Station

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'uid', 'restaurantName', 'foodCategory',
                  'station', 'latitude', 'longitude', 'distFromStation',
                  'phone', 'operatingHours', 'searchNum',
                  'likeNum', 'reviewNum', 'representativeImage', 'images')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    reviewImages = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'restaurant', 'content', 'created_at', 'uid', 'nickname', 'profileImageLink', 'reviewImages')

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ('station', 'latitude', 'longitude', 'distFromStation')