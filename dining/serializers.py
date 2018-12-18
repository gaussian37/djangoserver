# dining/serializers.py

from rest_framework import serializers
from .models import Restaurant, Like, Image, Review, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many = True, read_only = True)

    class Meta:
        model = Restaurant
        fields = ('id', 'restaurantName', 'foodCategory',
                  'station', 'longitude', 'latitude',
                  'phone', 'operatingHours', 'searchNum',
                  'likeNum', 'reviewNum', 'images')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'