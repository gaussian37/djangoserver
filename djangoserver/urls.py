"""djangoserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from .schema import *

urlpatterns = [
    path('admin/', admin.site.urls),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),     # DRF 페이지에서, 우측 상단에 login ID를 표시해 줍니다.
    url(r'^api-token-auth/$', obtain_auth_token),                                       # Token authorization

    url(r'^rest-auth/', include('rest_auth.urls')),                                     # django-allauth
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),           # django-allauth

    url(r'^api-jwt-auth/$', obtain_jwt_token),
    url(r'^api-jwt-auth/refresh/$', refresh_jwt_token),
    url(r'^api-jwt-auth/verify/$', verify_jwt_token),

    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^dining/v1/', include('dining.urls', namespace='dining/v1')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^swagger(?P<format>\.json|\.yaml)/v1$', schema_view_v1.without_ui(cache_timeout=0), name='schema-json'),
        url(r'^swagger/v1/$', schema_view_v1.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        url(r'^dining/v1/redoc/$', schema_view_v1.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),

        path('__debug__/', include(debug_toolbar.urls)),
    ]

