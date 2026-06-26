from django.core.paginator import Paginator

from constants import ITEMS_PER_PAGE




def get_page(entity_objects, request):
    paginator = Paginator(entity_objects, ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return page_obj