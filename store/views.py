import os

from django.http import JsonResponse

from logic.services import filtering_category
from .models import DATABASE
from django.http import HttpResponse
from logic.services import view_in_cart, add_to_cart, remove_from_cart


def products_view(request):
    if request.method == "GET":
        product_id = request.GET.get('id')

        if product_id in DATABASE:
            return JsonResponse(DATABASE.get(product_id), json_dumps_params={'ensure_ascii': False, 'indent': 4})

        if not product_id:
            category_key = request.GET.get("category")
            ordering_key = request.GET.get("ordering")
            reverse = request.GET.get("reverse") in ("true", "True")
            data = filtering_category(DATABASE, category_key, ordering_key, reverse)
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})
        else:
            return HttpResponse("Данного продукта нет в списке")


def products_page_view(request, page):
    if request.method == "GET":
        if isinstance(page, int):
            page = str(page)
            if page not in DATABASE:
                return HttpResponse(status=404)

            html_file = DATABASE.get(page).get('html')
            return get_html(f'store/products/{html_file}.html')

        if isinstance(page, str):
            for data in DATABASE.values():    #f'store/products/{page}.html'
                print(data)
                if data['html'] == page:
                    return get_html(f'store/products/{page}.html')
            return HttpResponse(status=404)


def get_html(html_path: str | os.PathLike) -> HttpResponse:
    with open(html_path, 'r', encoding="utf-8") as f:
        data = f.read()
    return HttpResponse(data)


def shop_view(request):
    if request.method == "GET":
        with open('store/shop.html', encoding="utf-8") as f:
            data = f.read()
        return HttpResponse(data)


def cart_view(request):
    if request.method == "GET":
        data = view_in_cart() # TODO Вызвать ответственную за это действие функцию
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                     'indent': 4})


def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(id_product)  # TODO Вызвать ответственную за это действие функцию
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(id_product)  # TODO Вызвать ответственную за это действие функцию
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})