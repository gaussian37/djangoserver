from rest_framework.pagination import PageNumberPagination

class RestaurantPageNumberPagination(PageNumberPagination):
    page_size = 20


class ReviewPageNumberPagination(PageNumberPagination):
    page_size = 20