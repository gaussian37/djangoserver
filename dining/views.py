# dining/views.py

from django.shortcuts import render
from rest_framework import viewsets
from .models import Restaurant, LikeRestaurant, Image, Review
from .serializers import RestaurantSerializer, LikeRestaurantSerializer, ImageSerializer, ReviewSerializer
from .pagination import RestaurantPageNumberPagination, ReviewPageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly



'''
RestaurantViewSet
- ListView
- DetailView
'''
class RestaurantViewSet(viewsets.ModelViewSet, generics.ListAPIView):

    '''
    Properties
    '''

    # authentication_classes = []

    # Restaurant는 인증이 된 경우만 POST가 가능하고 그렇지 않으면 Read만 가능하도록 설정
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # Restaurant DB에서 전체 field를 가져 온다.
    queryset = Restaurant.objects.all()
    
    # serializer class로 RestaurantSerializer 선정
    serializer_class = RestaurantSerializer
    
    # pagination로 기본값 6 페이지 선정
    pagination_class = RestaurantPageNumberPagination


    '''
    - Restaurant ListView 재 정의
    - foodCategory와 station 모두에 Parameter가 전달 되었을 경우, 조건 기반으로 조회한다.
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
    - Restaurant DetailView 재 정의
    - 특정 Restaurant를 조회하였을 때, 조회수가 +1 되도록 한다.
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




'''
LikeRestaurantViewSet
- ListView
    - uid 와 restaurant_id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
      
- 기본 DetailView 지원
    
'''
class LikeRestaurantViewSet(viewsets.ModelViewSet):

    '''
    Properties
    '''

    # "좋아요" 기능의 경우 인증이 된 유저만 사용 가능하도록 설정
    permission_classes = [IsAuthenticated]

    # "좋아요" 테이블에서 Object 들을 가져온다.
    queryset = LikeRestaurant.objects.all()

    # serializer class로 LikeRestaurantSerializer 선정
    serializer_class = LikeRestaurantSerializer


    '''
    - LikeRestaurantViewSet ListView 재 정의
        - uid 와 restaurant_id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
    '''
    def list(self, request, *args, **kwargs):
        # uid 파라미터, 조회 결과 없을 시 None 리턴
        uid = request.GET.get("uid", None)

        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)

        if uid is not None and restaurant_id is not None:
            self.queryset = self.queryset.filter(uid=uid, restaurant=restaurant_id)

        return super().list(request, *args, **kwargs)


'''
ImageViewSet
'''
class ImageViewSet(viewsets.ModelViewSet):
    '''
    Properties
    '''

    # "이미지" 쓰기 기능의 경우 인증이 된 유저만 사용 가능 / 읽기 기능의 경우는 인증 필요 없음
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # "이미지" 테이블에서 Object 들을 가져온다.
    queryset = Image.objects.all()

    # serializer class로 ImageSerializer 선정
    serializer_class = ImageSerializer

    # pagination로 기본값 6 페이지 선정
    pagination_class = ReviewPageNumberPagination


    '''
    - ReviewViewSet ListView 재 정의
        - restaurant_id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
    '''

    def list(self, request, *args, **kwargs):
        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)

        if restaurant_id is not None:
            self.queryset = self.queryset.filter(restaurant=restaurant_id)

        return super().list(request, *args, **kwargs)


    '''
    - ReviewViewSet DetailView 재 정의
        -  
    '''




'''
ReviewViewSet
'''
class ReviewViewSet(viewsets.ModelViewSet):
    '''
    Properties
    '''

    # "리뷰" 쓰기 기능의 경우 인증이 된 유저만 사용 가능 / 읽기 기능의 경우는 인증 필요 없음
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # "이미지" 테이블에서 Object 들을 가져온다.
    queryset = Review.objects.all()

    # serializer class로 ReviewSerializer 선정
    serializer_class = ReviewSerializer


    '''
    - Restaurant ListView 재 정의
    - foodCategory와 station 모두에 Parameter가 전달 되었을 경우, 조건 기반으로 조회한다.
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