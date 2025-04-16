from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'
