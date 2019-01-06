from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from django.conf.urls import url, include


schema_url_v1_patterns = [
    url(r'^dining/v1/', include('dining.urls', namespace='dining')),
]

schema_view_v1 = get_schema_view(
    openapi.Info(
        title="Dining API",
        default_version='v1',
        description="bluemen의 Dining API 문서 페이지 입니다.",
        # terms_of_service =
        contact=openapi.Contact(email="service.blumen@google.com"),
        license=openapi.License(name="bluemen"),
    ),
    validators=['flex'],  # 'ssv'],
    public=True,
    permission_classes=(AllowAny,),
    patterns=schema_url_v1_patterns,
)