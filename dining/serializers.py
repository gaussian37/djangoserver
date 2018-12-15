# dining/serializers.py

from rest_framework import serializers
from .models import Restaurant, LikeRestaurant, Image, Review

class RestaurantAllSerializer(serializers.ModelSerializer):
    class Meta:
        pass


# class RestaurantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Restaurant
#         fields = ('id', 'restaurantName', 'foodCategory', 'station', 'longitude', 'latitude', 'phone', 'operatingHours', 'searchNum')

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class LikeRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeRestaurant
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'