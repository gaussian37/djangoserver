# dining/serializers.py

from rest_framework import serializers
from .models import Restaurant, LikeRestaurant

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class LikeRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeRestaurant
        fields = '__all__'
