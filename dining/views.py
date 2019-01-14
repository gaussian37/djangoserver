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
from .utils import dist, image_base_url

class RestaurantViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    """
    Restaurant 관련 REST API 기능 제공
    """

    # authentication_classes = []

    # Restaurant는 인증이 된 경우만 POST가 가능하고 그렇지 않으면 Read만 가능하도록 설정
    # permission_classes = [IsAuthenticatedOrReadOnly]

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


    def list(self, request, *args, **kwargs):
        '''
        음식 카테고리/역/정렬순 기준 해당 식당 리스트를 읽어오는 API

        ---
        + parameters :
            + `foodCategory` : 아래 리스트 중 한 개를 선택해야 합니다.
                + 삼겹살, 소고기, 회/해산물, 족발/보쌈, 곱창, 스테이크, 이자카야, 맥주, 칵테일, 와인
            + `station` : 지하철 역 이름을 선택해야 하고 끝에 **역은 생략** 합니다.
                + 강남, 사당, 수원 ...
            + `ordering`을 통하여 likeNum/reviewNum/searchNum/distFromStation 기준으로 조회합니다.
                + **likeNum** : 좋아요 (내림차순, 기본값)
                + **reviewNum** : 리뷰 갯수 (내림차순)
                + **searchNum** : 조회수 (내림차순)
                + **distFromStation** : 식당과 역과의 거리 (오름 차순)
        + use cases :
            + foodCategory=삼겹살, station=강남, ordering=likeNum
            + foodCategory=곱창, station=사당, ordering=distFromStation
        '''

        # foodCategory 파라미터, 조회 결과 없을 시 None 리턴
        foodCategory = request.GET.get("foodCategory", None)
        # station 파라미터, 조회 결과 없을 시 None 리턴
        station = request.GET.get("station", None)
        # ordering 파라미터, 조회 결과 없을 시
        ordering = request.GET.get("ordering", "likeNum")

        # foodCategory와 station 모두 값을 받았을 경우 :
        # foodCategory와 station을 기준으로 조회한 후 결과를 return 한다.
        if foodCategory is not None and station is not None:

            # foodCategory와 station을 기준으로 query를 filter한 결과를 받습니다.
            self.queryset = self.queryset.filter(foodCategory=foodCategory, station=station)

            # 입력 받은 정렬순의 내림차순으로 정렬하고 동일 순위 시 최신순으로 보여줍니다.
            if ordering == "distFromStation":
                # 거리순으로 정렬할 때에는 오름차순으로 정렬해야 합니다.
                self.queryset = self.queryset.order_by(ordering, "-id")
            else :
                # 거리 이외의 정렬 기준은 내림차순으로 정렬해야 합니다.
                self.queryset = self.queryset.order_by("-" + ordering, "-id")

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        '''
        식당 id를 입력하여 식당의 상세 정보를 조회하는 API

        ---
        + parameter :
            + Restaurant id
                + id에 해당하는 식당을 조회하였을 때, 조회수가 +1이 됩니다.
        '''

        # pk값 가져옴
        pk = self.kwargs['pk']
        # pk에 해당하는 object를 가져옴
        qs = Restaurant.objects.get(id=pk)

        # 조회되었을 때 조회수(searchNum)을 1 증가시켜준다.
        # 의도적인 조회수 증가를 제한하기 위해 throttling을 걸어준다.
        qs.searchNum += 1
        qs.save()

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        '''
        새로운 식당을 등록하는 API

        ---
        + parameters
            + `restaurantName` : 식당 이름 (**필수**)
            + `foodCategory` : 음식 카테고리 (**필수**)
            + `station` : 역 (**필수**)
            + `latitude` : 위도 (**필수**)
            + `longitude` : 경도 (**필수**)
            + phone : 전화번호 (선택)
            + operatingHours : 운영 시간 (선택)
        '''

        # request.data를 통하여 사용자가 입력한 값을 불러 옵니다.
        data = request.data.dict()
        # 사용자가 입력한 위도/경도/역 정보를 가져 옵니다.
        lat, long, station = float(data["latitude"]), float(data["longitude"]), data["station"]
        # 위도/경도/역 정보를 이용하여 식당과 역 사이의 거리를 구합니다.
        distFromStation = dist(lat, long, station)

        # request.data를 변경 가능하도록 만듭니다.
        request.POST._mutable = True
        # request.data에 식당과 역까지의 거리 입력합니다.
        request.POST['distFromStation'] = distFromStation

        return super().create(request, *args, **kwargs)

    def saveLikeReviewNum(self, qs, param, types):
        '''
        queryset에 해당하는 Restaurant의 likeNum과 ReviewNum을 갱신하는 함수

        ---
        + qs : QuerySet
        + param : like/review를 입력 받으며 입력받은 Num을 갱신합니다.
        + types : qs가 Query 인지 Model 인지 전달해 줍니다.
        '''

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

    def saveDistanceFromStation(self, qs, station, types):
        '''
        qs의 Restaurant을 station 간의 직선 거리를 갱신 합니다. 최초 한번만 갱신 됩니다.

        ---
        + qs : QuerySet
        + station : 역
        + types : qs가 Query 인지 Model 인지 전달해 줍니다.
        '''


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

class LikeViewSet(viewsets.ModelViewSet):
    '''
    Like 관련 REST API 기능 제공
    '''

    # "좋아요" 기능의 경우 인증이 된 유저만 사용 가능하도록 설정
    # permission_classes = [IsAuthenticated]

    # "좋아요" 테이블에서 Object 들을 Restaurant와 join 해서 가져온다.
    queryset = Like.objects.all().select_related('restaurant')

    # serializer class로 LikeRestaurantSerializer 선정
    serializer_class = LikeSerializer

    def list(self, request, *args, **kwargs):
        '''
        사용자가 어떤 식당에 좋아요를 하였는지 확인하는 API

        ---
        + parameters :
            + `uid` : 사용자의 uid를 입력합니다. (**필수**)
            + `restaurant-id` : 식당 id를 입력 합니다. (**필수**)
        + use cases :
            + uid='123', restaurant-id=1 이면 '123' 사용자가 식당 1에 좋아요를 눌렀으면 `result`에 결과가 반환됩니다.
            + 만약 좋아요를 누르지 않았다면 빈 리스트가 반환됩니다.
            + 좋아요를 누를 때/취소할 때, 어떤 사용자의 어떤 식당에 대한 좋아요 상태를 체크해야 정보가 동기화 됩니다.
        '''

        # uid 파라미터, 조회 결과 없을 시 None 리턴
        uid = request.GET.get("uid", None)

        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)

        if uid is not None and restaurant_id is not None:
            self.queryset = self.queryset.filter(uid=uid, restaurant=restaurant_id)

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        '''
        좋아요 등록 API

        ---
        + parameters :
            + `uid` : 사용자의 uid를 입력합니다. (**필수**)
            + `restaurant-id` : 식당 id를 입력 합니다. (**필수**)
        + create 시 해당 restaurant의 likeNum을 +1 합니다.
        '''
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
        '''
        좋아요를 취소하는 API

        ---
        + parameters
            + `id` : 좋아요 id (**필수**)
        + 좋아요를 취소할 때에는 반드시 좋아요를 하였는지 먼저 확인이 필요 합니다.
        + 좋아요를 취소하면 해당 식당의 likeNum이 -1 됩니다.
        '''
        # 삭제 할 instance의 pk값을 구합니다.
        pk = self.kwargs['pk']
        # pk 값을 이용하여 해당 Restaurant Object를 구합니다.
        q = Like.objects.get(id=pk)
        # Restaurant object 를 할당합니다.
        restaurant = q.restaurant
        # 할당 받은 Restaurant의 likeNum을 -1 해줍니다.
        self.setRestaurantLikeNum(restaurant, -1)

        return super().destroy(request, *args, **kwargs)

    def setRestaurantLikeNum(self, restaurant, offset):
        '''
        Like를 create/destroy 할 때, 해당하는 Restaurant의 likeNum을 update(+1/-1) 해주는 함수

        ---
        + parameters :
            + restaurant : restaurant object
            + offset : +1 / -1
        '''
        restaurant.likeNum += offset
        restaurant.save()

class ImageViewSet(viewsets.ModelViewSet):
    '''
    Image 관련 REST API 제공
    '''

    # "이미지" 쓰기 기능의 경우 인증이 된 유저만 사용 가능 / 읽기 기능의 경우는 인증 필요 없음
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # "이미지" 테이블에서 Object 들을 가져온다.
    queryset = Image.objects.all()

    # serializer class로 ImageSerializer 선정
    serializer_class = ImageSerializer

    # pagination로 기본값 6 페이지 선정
    pagination_class = ReviewPageNumberPagination


    def list(self, request, *args, **kwargs):
        '''
        식당 id/리뷰 id로 해당 이미지 전체 리스트를 조회하는 API

        ---
        + parameters :
            + restaurant-id : 식당 id에 해당하는 전체 이미지 리스트를 조회 (**restaurant-id 또는 review-id 하나 필수**)
            + review-id : 리뷰 id에 해당하는 전체 이미지 리스트를 조회 (**restaurant-id 또는 review-id 하나 필수**)
        '''
        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)
        review_id = request.GET.get("review-id", None)

        if restaurant_id is not None:
            self.queryset = self.queryset.filter(restaurant=restaurant_id)
        elif review_id is not None:
            self.queryset = self.queryset.filter(review=review_id)

        return super().list(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        '''
        특정 사진을 제거하는 API

        ---
        + parameters :
            + id : 이미지 id
        + 삭제하려는 이미지가 대표 이미지와 같다면 해당 이미지 식당의 RepresentativeImage를 지우고 삭제 합니다.
        '''
        # 삭제 할 instance의 pk값을 구합니다.
        pk = self.kwargs['pk']
        # pk 값을 이용하여 해당 image instance를 가져 옵니다.
        q = Image.objects.get(id=pk)
        # Instance에서 image url을 가져 옵니다.
        image_url = image_base_url + q.image.name

        # Instance의 restaurant-id를 가져 옵니다.
        restaurant_id = q.restaurant_id
        # image에 해당하는 restaurant instance를 할당합니다.
        restaurant = Restaurant.objects.get(id=restaurant_id)

        # 현재 제거하려하는 이미지가 대표 이미지라면 Restaurant instance에서 대표 이미지를 삭제합니다.
        print(restaurant.representativeImage)
        if image_url == restaurant.representativeImage:
            restaurant.representativeImage = ""
            restaurant.save()

        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Restaurnat의 Review를 read/create/delete 하는 API
    """

    # "리뷰" 쓰기 기능의 경우 인증이 된 유저만 사용 가능 / 읽기 기능의 경우는 인증 필요 없음
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # "이미지" 테이블에서 Object 들을 가져온다.
    queryset = Review.objects.all().select_related("restaurant")

    # serializer class로 ReviewSerializer 선정
    serializer_class = ReviewSerializer

    def list(self, request, *args, **kwargs):
        '''
        review 리스트를 불러오는 API

        ---
        + parameters :
            + `uid` : uid에 해당하는 전체 리뷰 리스트를 조회 (**uid 또는 restaurant-id 하나 필수**)
            + `restaurant-id` : 리뷰 id에 해당하는 전체 리뷰 리스트를 조회 (**uid 또는 restaurant-id 하나 필수**)
        + 리턴 시 최신 등록일 기준 정렬하여 반환
            + review 등록 시 Image가 같이 등록되어야 합니다.
            + 앱에서 review를 먼저 등록 하고 uid로 한번 조회하면 가장 최근에 등록된 review의 id를 받아옵니다.
            + 이 때 받아온 review id를 이미지를 등록할 때 사용합니다.
        '''

        # uid 파라미터, 조회 결과 없을 시 None 리턴
        uid = request.GET.get("uid", None)

        # restaurant-id 파라미터, 조회 결과 없을 시 None 리턴
        restaurant_id = request.GET.get("restaurant-id", None)

        # uid 또는 restaurant-id로 조회
        if uid is not None :
            self.queryset = self.queryset.filter(uid=uid).order_by("-created_at", "-id")
        elif restaurant_id is not None:
            self.queryset = self.queryset.filter(restaurant=restaurant_id).order_by("-created_at", "-id")

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        '''
        리뷰 생성 API

        ---
        + parameters :
            + `content` : 리뷰 본문을 입력합니다. (**필수**)
            + `uid` : 리뷰 작성자의 uid를 입력합니다. (**필수**)
            + `restaurant-id` : 식당 id를 입력합니다. (**필수**)
        + 리뷰 생성 시 해당 Restaurant의 reviewNum을 +1 합니다.
        '''
        # 입력 받은 데이터 접근
        data = request.data.dict()
        # 입력 받은 데이터 중 restaurnat(식당 id)를 이용하여 Restaurant Object 확인
        restaurant = Restaurant.objects.get(id = data["restaurant-id"])
        # 할당 받은 Restaurant의 reviewNum을 +1 해줍니다.
        self.setRestaurantreviewNum(restaurant, 1)

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        '''
        리뷰 삭제 API

        ---
        + parameters :
            + `id` : 리뷰 id를 입력합니다.. (**필수**)
        + 리뷰 삭제 시 해당 Restaurant의 reviewNum을 -1 합니다.
        '''
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

class UserViewSet(viewsets.ModelViewSet):
    '''
    사용자 정보에 관한 REST API
    '''

    # "User" 기능의 경우 인증이 된 유저만 사용 가능
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # User 테이블에서 Object 들을 가져온다.
    queryset = User.objects.all()

    # serializer class로 ReviewSerializer 선정
    serializer_class = UserSerializer
