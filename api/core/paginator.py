from rest_framework.pagination import PageNumberPagination
import math


class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of products per page
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, **kwargs):
        page_size = self.get_page_size(self.request)
        total_pages = math.ceil(self.page.paginator.count / page_size) if page_size else 1
        return {
            'count': self.page.paginator.count,  # Total number of products
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': total_pages,  # Total number of pages
        }
