# dining/urls.py

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dining/v1'

router = DefaultRouter()
router.register(r'users', views.UsersViewSet)
router.register(r'restaurant', views.RestaurantViewSet)
router.register(r'like', views.LikeViewSet)
router.register(r'image', views.ImageViewSet)
router.register(r'review', views.ReviewViewSet)
router.register(r'station', views.StationViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]