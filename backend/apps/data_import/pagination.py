# 文件: backend/apps/data_import/pagination.py
from rest_framework.pagination import PageNumberPagination

from .responses import ok


class StandardPagination(PageNumberPagination):
    # 统一使用 settings.REST_FRAMEWORK.PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return ok({
            "results": data,
            "page": self.page.number,
            "page_size": self.page.paginator.per_page,
            "total_pages": self.page.paginator.num_pages,
            "total_items": self.page.paginator.count
        })
