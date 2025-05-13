from rest_framework.pagination import PageNumberPagination
from django.conf import settings

class DishPaginator(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK['PAGE_SIZE']