from rest_framework.pagination import PageNumberPagination


class Paginator:
    paginator = PageNumberPagination()

    def __init__(self, records, request):
        """
        Method that pagiginate all the records
        """
        self.records = records
        self.request = request

    def paginate(self, no_of_record: int):
        self.paginator.page_size = no_of_record
        result_page = self.paginator.paginate_queryset(self.records, self.request)
        return self.paginator.get_paginated_response(result_page)
    


class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = "page_size"
    max_page_size = 100 