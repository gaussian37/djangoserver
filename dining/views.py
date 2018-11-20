# dining/views.py

from django.shortcuts import render
from rest_framework import viewsets
from .models import Restaurant, FoodImage, RestaurantImage, MenuImage
from .serializers import RestaurantSerializer
from .pagination import RestaurantPageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


# Restaurant의 ListView, DetailView 지원
class RestaurantViewSet(viewsets.ModelViewSet, generics.ListAPIView):

    # authentication_classes = []
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Restaurant DB에서 전체 field를 가져 온다.
    queryset = Restaurant.objects.all()
    
    # serializer class로 RestaurantSerializer 선정
    serializer_class = RestaurantSerializer
    
    # pagination로 기본값 20 페이지 선정
    pagination_class = RestaurantPageNumberPagination


    '''
    Restaurant list 조회 재정의
    foodCategory와 station 모두에 Parameter가 전달 되었을 경우, 조건 기반으로 조회한다.
    '''
    def list(self, request, *args, **kwargs):

        # foodCategory 파라미터, 조회 결과 없을 시 None 리턴
        foodCategory = request.GET.get("foodCategory", None)
        # station 파라미터, 조회 결과 없을 시 None 리턴
        station = request.GET.get("station", None)

        # 위치 정보(위도 : latitude, 경도 : longitude) 파라미터, 조회 결과 없을 시 None 리턴
        latitude = request.GET.get("latitude", None)
        longitude = request.GET.get("longitude", None)

        '''
        파라미터 상태에 따라 조회 방법 변경
        1. foodCategory & station 기준으로 조회
        2. restarurantName? 위도/경도 기준으로 가까운 거리 순으로 리턴
        '''
        ## foodCategory와 station 모두 값을 받았을 경우 : foodCategory와 station을 기준으로 조회한 후 결과를 return 한다.
        if foodCategory is not None and station is not None:
            self.queryset = self.queryset.filter(foodCategory=foodCategory, station=station)
        else:
            pass

        return super().list(request, *args, **kwargs)

    '''
    Restaurant detail 조회 재정희
    특정 Restaurant를 조회하였을 때, 조회수가 +1 되도록 한다.
    '''

    def retrieve(self, request, *args, **kwargs):
        # pk값 가져옴
        pk = self.kwargs['pk']
        # pk에 해당하는 object를 가져옴
        restaurantObject = Restaurant.objects.get(id=pk)

        # 조회되었을 때 조회수(searchNum)을 1 증가시켜준다.
        # 의도적인 조회수 증가를 제한하기 위해 throttling을 걸어준다.
        restaurantObject.searchNum += 1
        restaurantObject.save()

        return super().retrieve(request, *args, **kwargs)


    # '''세부 API 사용 시 아래 참조'''
    # @action(detail=False)
    # def main_search(self, request):
    #     foodCategory = request.GET.get("foodCategory")
    #     station = request.GET.get("station")
    #
    #     # foodCategory와 station을 기준으로 filter한 쿼리셋
    #     qs = self.queryset.filter(foodCategory=foodCategory, station=station)
    #     #
    #     serializer = self.get_serializer(qs, many=True)
    #     print(serializer.data)
    #     return Response(serializer.data)