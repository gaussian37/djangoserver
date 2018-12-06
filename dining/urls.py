# dining/urls.py

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dining'

router = DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet)
router.register(r'like-restaurant', views.LikeRestaurantViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]