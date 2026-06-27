from django.core.paginator import Paginator

from constants import ITEMS_PER_PAGE


def get_page(entity_objects, request, items_per_page=ITEMS_PER_PAGE):
    paginator = Paginator(entity_objects, items_per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
