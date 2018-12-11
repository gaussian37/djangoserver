from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class PostAdminRestaurant(admin.ModelAdmin):
    pass