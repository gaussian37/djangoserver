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


class RestaurantViewSet(viewsets.ModelViewSet, generics.ListAPIView):

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

        # foodCategory 파라미터
        foodCategory = request.GET.get("foodCategory")
        # station 파라미터
        station = request.GET.get("station")

        # 파라미터가 올바르게 입력 되었는지 확인
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
        restaurantObject = Restaurant.objects.get(id=pk)
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