from rest_framework.pagination import PageNumberPagination

class RestaurantPageNumberPagination(PageNumberPagination):
    page_size = 6


class ReviewPageNumberPagination(PageNumberPagination):
    page_size = 6