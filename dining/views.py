# dining/views.py

from django.shortcuts import render
from rest_framework import viewsets
from .models import Restaurant, Like, Image, Review, User
from .serializers import RestaurantSerializer, LikeSerializer, ImageSerializer, ReviewSerializer, UserSerializer
from .pagination import RestaurantPageNumberPagination, ReviewPageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .utils import dist


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

    # Restaurant DB에서 전체 field를 가져올 때 prefetch_related로 가져온다.
    queryset = Restaurant.objects.all().prefetch_related(
        "like_set",
        "review_set",
        "images",
    )
    
    # serializer class로 RestaurantSerializer 선정
    serializer_class = RestaurantSerializer
    
    # pagination로 기본값 6 페이지 선정
    pagination_class = RestaurantPageNumberPagination


    '''
    - Restaurant ListView 재 정의
    - foodCategory와 station 모두에 Parameter가 전달 되었을 경우, 조건 기반으로 조회한다.
    - ordering을 통하여 조회순서를 (likeNum/reviewNum/searchNum) 내림차순으로 정한다. (default = likeNum)
      distance는 역의 위치와의 직선 거리를 기준으로 내림차순으로 조회한다.
    '''
    def list(self, request, *args, **kwargs):

        # foodCategory 파라미터, 조회 결과 없을 시 None 리턴
        foodCategory = request.GET.get("foodCategory", None)
        # station 파라미터, 조회 결과 없을 시 None 리턴
        station = request.GET.get("station", None)

        # ordering 파라미터, 조회 결과 없을 시
        ordering = request.GET.get("ordering", "likeNum")

        # foodCategory와 station 모두 값을 받았을 경우 :
        # foodCategory와 station을 기준으로 조회한 후 결과를 return 한다.
        print(foodCategory, station)
        if foodCategory is not None and station is not None:

            # foodCategory와 station을 기준으로 query를 filter한 결과를 받습니다.
            self.queryset = self.queryset.filter(foodCategory=foodCategory, station=station)

            qs = self.queryset
            # Like/Review/Distance 를 갱신합니다. (Distance는 최초 한번 갱신 됩니다.)
            self.updateLikeReviewDistNum(qs, station, "query")

            # 입력 받은 정렬순의 내림차순으로 정렬하고 동일 순위 시 최신순으로 보여줍니다.
            self.queryset = self.queryset.order_by("-" + ordering, "-id")

        return super().list(request, *args, **kwargs)


    '''
    - Restaurant DetailView 재 정의
    - 특정 Restaurant를 조회하였을 때, 조회수가 +1 되도록 한다.
    '''
    def retrieve(self, request, *args, **kwargs):
        # pk값 가져옴
        pk = self.kwargs['pk']
        # pk에 해당하는 object를 가져옴
        qs = Restaurant.objects.get(id=pk)

        # 조회되었을 때 조회수(searchNum)을 1 증가시켜준다.
        # 의도적인 조회수 증가를 제한하기 위해 throttling을 걸어준다.
        qs.searchNum += 1
        qs.save()

        return super().retrieve(request, *args, **kwargs)

    '''
    - Restaurant create 재 정의
    - create 시 입력 받은 위도/경도/역 정보를 이용하여 역으로 부터 식당의 거리를 계산하여 입력한다.
    '''
    def create(self, request, *args, **kwargs):

        data = request.data.dict()
        lat, long, station = float(data["latitude"]), float(data["longitude"]), data["station"]
        distFromStation = dist(lat, long, station)

        request.POST._mutable = True
        request.POST['distFromStation'] = distFromStation

        return super().create(request, *args, **kwargs)


    '''
    queryset에 해당하는 Restaurant의 likeNum과 ReviewNum을 갱신하는 함수
    - qs : QuerySet
    - param : like/review를 입력 받으며 입력받은 Num을 갱신합니다.
    - types : qs가 Query 인지 Model 인지 전달해 줍니다.
    '''
    def saveLikeReviewNum(self, qs, param, types):

        if types == "model":
            if param == "like":
                qs.likeNum = len(qs.like_set.all())
                qs.save()
            elif param == "review":
                qs.reviewNum = len(qs.review_set.all())
                qs.save()

        elif types == "query":
            # 각 restaurant의 like/review 수를 가져옵니다.
            for q in qs:
                # Like/Review 테이블에서 각 식당별로 조회한 갯수를 저장합니다.
                # likeNum/reviewNum에 저장된 결과를 ListView 호출 시 반환합니다.
                if param == "like":
                    q.likeNum = len(q.like_set.all())
                    q.save()
                elif param == "review":
                    q.reviewNum = len(q.review_set.all())
                    q.save()

    '''
    qs의 Restaurant을 station 간의 직선 거리를 갱신 합니다. 최초 한번만 갱신 됩니다.
    - qs : QuerySet
    - station : 역
    - types : qs가 Query 인지 Model 인지 전달해 줍니다.
    '''
    def saveDistanceFromStation(self, qs, station, types):

        if types == "model":
            if qs.distFromStation < 0:
                qs.distFromStation = dist(qs.latitude, qs.longitude, station)
                qs.save()

        elif types == "query":
            # 입력받은 station을 기준으로 restaurant와 station간의 직선 거리를 구합니다.
            for q in qs:
                if q.distFromStation < 0:
                    q.distFromStation = dist(q.latitude, q.longitude, station)
                    q.save()


    '''
    Like/Review/Dist 전체를 갱신 합니다.
    - qs : QuerySet
    - station : 역
    - types : qs가 Query 인지 Model 인지 전달해 줍니다.
    '''
    def updateLikeReviewDistNum(self, qs, station, types):
        # 각 restaurant의 like 수를 갱신합니다.
        self.saveLikeReviewNum(qs, 'like', types)

        # 각 restaurant의 review 수를 갱신합니다.
        self.saveLikeReviewNum(qs, 'review', types)

        # 각 restaurant의 station으로 부터의 거리수를 갱신 합니다.
        self.saveDistanceFromStation(qs, station, types)


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
LikeViewSet
- list
    - uid 와 restaurant-id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
    - create 하기 전 어떤 사용자가 특정 식당에 좋아요를 하였는 지 여부를 확인 하기 위함
- create
    - uid와 restaurant-id를 입력하여 Like를 생성함
    - create 시 해당 restaurant의 likeNum을 +1 함
- destroy
    - Like instance의 pk 값을 이용하여 삭제
    - destroy 시 해당 restaurant의 likeNum을 -1 함
- setRestaurantLikeNum
    - Like를 create/destroy 할 때, 해당하는 Restaurant의 likeNum을 update(+1/-1) 해주는 함수
'''
class LikeViewSet(viewsets.ModelViewSet):

    # "좋아요" 기능의 경우 인증이 된 유저만 사용 가능하도록 설정
    # permission_classes = [IsAuthenticated]

    # "좋아요" 테이블에서 Object 들을 Restaurant와 join 해서 가져온다.
    queryset = Like.objects.all().select_related('restaurant')

    # serializer class로 LikeRestaurantSerializer 선정
    serializer_class = LikeSerializer

    '''
    - LikeViewSet ListView 재정의
        - uid 와 restaurant-id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
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
    - LikeViewSet create 재정의
    - 입력되는 값 중 restaurant(식당 id) 값으로 filter하여 얻은 Restaurant Object로 Restaurnat를 접근합니다.
      즉, Like에 해당하는 Restaurant에 접근합니다. 그리고 Restaurant의 likeNum을 +1 합니다.
    '''
    def create(self, request, *args, **kwargs):
        # 입력 받은 데이터 접근
        data = request.data.dict()
        # 입력 받은 데이터 중 restaurnat(식당 id)를 이용하여 Restaurant Object 확인
        restaurant = Restaurant.objects.get(id = data["restaurant"])
        # 할당 받은 Restaurant의 likeNum을 +1 해줍니다.
        self.setRestaurantLikeNum(restaurant, 1)

        return super().create(request, *args, **kwargs)

    '''
    - LikeViewSet destroy 재정의
    - 삭제 할 좋아요 instance의 pk 값을 이용하여 삭제 할 때, 해당 Restaurant의 objectdml likeNum을 -1 합니다.
    '''
    def destroy(self, request, *args, **kwargs):
        # 삭제 할 instance의 pk값을 구합니다.
        pk = self.kwargs['pk']
        # pk 값을 이용하여 해당 Restaurant Object를 구합니다.
        q = Like.objects.get(id=pk)
        # Restaurant object 를 할당합니다.
        restaurant = q.restaurant
        # 할당 받은 Restaurant의 likeNum을 -1 해줍니다.
        self.setRestaurantLikeNum(restaurant, -1)

        return super().destroy(request, *args, **kwargs)

    '''
    - Like를 create/destroy 할 때, 해당하는 Restaurant의 likeNum을 update(+1/-1) 해주는 함수
    - restaurant : restaurant object
    - offset : +1 / -1
    '''
    def setRestaurantLikeNum(self, restaurant, offset):
        restaurant.likeNum += offset
        restaurant.save()


'''
ImageViewSet
- List
    - restaurant-id 파라미터 입력을 이용하여 GET 요청 시 해당 restaurant에 해당하는 전체 image list를 반환함
    - review-id 파라미터 입력을 이용하여 GET 요청 시 해당 review에 해당하는 전체 image list를 반환함
- destroy
    - 삭제하려는 이미지가 대표 이미지와 같다면 Restaurant Instance에서 
      RepresentativeImage를 지우고 삭제 합니다.      
'''
class ImageViewSet(viewsets.ModelViewSet):

    # "이미지" 쓰기 기능의 경우 인증이 된 유저만 사용 가능 / 읽기 기능의 경우는 인증 필요 없음
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # "이미지" 테이블에서 Object 들을 가져온다.
    queryset = Image.objects.all()

    # serializer class로 ImageSerializer 선정
    serializer_class = ImageSerializer

    # pagination로 기본값 6 페이지 선정
    pagination_class = ReviewPageNumberPagination

    # image base url
    image_base_url = "http://localhost:8000/media/"

    '''
    - list 재정의
        - restaurant_id 파라미터 입력을 이용하여 GET 요청 시 해당 restaurant에 해당하는 전체 image list를 반환함
        - review_id 파라미터 입력을 이용하여 GET 요청 시 해당 review에 해당하는 전체 image list를 반환함
    '''
    def list(self, request, *args, **kwargs):
        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)
        review_id = request.GET.get("review-id", None)

        if restaurant_id is not None:
            self.queryset = self.queryset.filter(restaurant=restaurant_id)
        elif review_id is not None:
            self.queryset = self.queryset.filter(review=review_id)

        return super().list(request, *args, **kwargs)

    '''
    - destroy 재정의
    - 삭제하려는 이미지가 대표 이미지와 같다면 Restaurant Instance에서 
      RepresentativeImage를 지우고 삭제 합니다.          
    '''
    def destroy(self, request, *args, **kwargs):
        # 삭제 할 instance의 pk값을 구합니다.
        pk = self.kwargs['pk']
        # pk 값을 이용하여 해당 image instance를 가져 옵니다.
        q = Image.objects.get(id=pk)
        # Instance에서 image url을 가져 옵니다.
        image_url = self.image_base_url + q.image.name

        # Instance의 restaurant-id를 가져 옵니다.
        restaurant_id = q.restaurant_id
        # image에 해당하는 restaurant instance를 할당합니다.
        restaurant = Restaurant.objects.get(id=restaurant_id)

        # 현재 제거하려하는 이미지가 대표 이미지라면 Restaurant instance에서 대표 이미지를 삭제합니다.
        print(image_url)
        print(restaurant.representativeImage)
        if image_url == restaurant.representativeImage:
            restaurant.representativeImage = ""
            restaurant.save()

        return super().destroy(request, *args, **kwargs)


'''
ReviewViewSet
- list
    - uid 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함 
    - restaurant-id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
- create
    - uid와 restaurant-id를 입력하여 Like를 생성함
    - create 시 해당 restaurant의 likeNum을 +1 함
- destroy
    - Like instance의 pk 값을 이용하여 삭제
    - destroy 시 해당 restaurant의 likeNum을 -1 함
- setRestaurantLikeNum
    - Like를 create/destroy 할 때, 해당하는 Restaurant의 likeNum을 update(+1/-1) 해주는 함수

'''
class ReviewViewSet(viewsets.ModelViewSet):

    # "리뷰" 쓰기 기능의 경우 인증이 된 유저만 사용 가능 / 읽기 기능의 경우는 인증 필요 없음
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # "이미지" 테이블에서 Object 들을 가져온다.
    queryset = Review.objects.all().select_related("restaurant")

    # serializer class로 ReviewSerializer 선정
    serializer_class = ReviewSerializer

    '''
    - list
        - uid 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함 
        - restaurant-id 파라미터 입력을 이용하여 GET 요청 시 해당 list를 반환함
    '''
    def list(self, request, *args, **kwargs):
        # uid 파라미터, 조회 결과 없을 시 None 리턴
        uid = request.GET.get("uid", None)

        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)

        if uid is not None :
            self.queryset = self.queryset.filter(uid=uid)
        elif restaurant_id is not None:
            self.queryset = self.queryset.filter(restaurant=restaurant_id)

        return super().list(request, *args, **kwargs)

    '''
    - create
        - 입력되는 값 중 restaurant(식당 id) 값으로 filter하여 얻은 Restaurant Object로 Restaurnat를 접근합니다.
          즉, Reivew에 해당하는 Restaurant에 접근합니다. 그리고 Restaurant의 reviewNum을 +1 합니다.
    '''
    def create(self, request, *args, **kwargs):
        # 입력 받은 데이터 접근
        data = request.data.dict()
        # 입력 받은 데이터 중 restaurnat(식당 id)를 이용하여 Restaurant Object 확인
        restaurant = Restaurant.objects.get(id = data["restaurant"])
        # 할당 받은 Restaurant의 reviewNum을 +1 해줍니다.
        self.setRestaurantreviewNum(restaurant, 1)

        return super().create(request, *args, **kwargs)

    '''
    - destroy
        - 삭제 할 review instance의 pk 값을 이용하여 삭제 할 때, 해당 Restaurant의 objectdml reviewNum을 -1 합니다.
    '''
    def destroy(self, request, *args, **kwargs):
        # 삭제 할 instance의 pk값을 구합니다.
        pk = self.kwargs['pk']
        # pk 값을 이용하여 해당 Restaurant Object를 구합니다.
        q = Review.objects.get(id=pk)
        # Restaurant object 를 할당합니다.
        restaurant = q.restaurant
        # 할당 받은 Restaurant의 reviewNum을 -1 해줍니다.
        self.setRestaurantreviewNum(restaurant, -1)

        return super().destroy(request, *args, **kwargs)


    '''
    - Review를 create/destroy 할 때, 해당하는 Restaurant의 reviewNum을 update(+1/-1) 해주는 함수
    - restaurant : restaurant object
    - offset : +1 / -1
    '''
    def setRestaurantreviewNum(self, restaurant, offset):
        restaurant.reviewNum += offset
        restaurant.save()

'''
UserViewSet
'''
class UserViewSet(viewsets.ModelViewSet):
    '''
    Properties
    '''

    # "User" 기능의 경우 인증이 된 유저만 사용 가능
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # User 테이블에서 Object 들을 가져온다.
    queryset = User.objects.all()

    # serializer class로 ReviewSerializer 선정
    serializer_class = UserSerializer