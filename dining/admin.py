from django.contrib import admin
from .models import Restaurant, FoodImage, RestaurantImage, MenuImage

@admin.register(Restaurant)
class PostAdminRestaurant(admin.ModelAdmin):
    pass

@admin.register(FoodImage)
class PostAdminFoodImage(admin.ModelAdmin):
    pass

@admin.register(RestaurantImage)
class PostAdminRestaurantImage(admin.ModelAdmin):
    pass

@admin.register(MenuImage)
class PostAdminMenuImage(admin.ModelAdmin):
    pass
