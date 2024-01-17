import os

from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound


from logic.services import filtering_category

from django.http import HttpResponse
from logic.services import view_in_cart, add_to_cart, remove_from_cart
from store.models import DATABASE
from django.shortcuts import redirect, render


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
        if isinstance(page, str):
            for data in DATABASE.values():
                if data['html'] == page:
                    return render(request, "store/product.html", context={"product": data})

        elif isinstance(page, int):
            # Обрабатываем условие того, что пытаемся получить страницу товара по его id
            data = DATABASE.get(str(page))  # Получаем какой странице соответствует данный id
            if data:
                return render(request, "store/product.html", context={"product": data})

        return HttpResponse(status=404)


def get_html(html_path: str | os.PathLike) -> HttpResponse:
    with open(html_path, 'r', encoding="utf-8") as f:
        data = f.read()
    return HttpResponse(data)


def shop_view(request):
    if request.method == "GET":
        category_key = request.GET.get("category")
        if ordering_key := request.GET.get("ordering"):
            if request.GET.get("reverse") in ('true', 'True'):
                data = filtering_category(DATABASE, category_key, ordering_key,
                                          True)
            else:
                data = filtering_category(DATABASE, category_key, ordering_key)
        else:
            data = filtering_category(DATABASE, category_key)
        return render(request, 'store/shop.html',
                      context={"products": data,
                               "category": category_key})



@login_required(login_url='login:login_view')
def cart_view(request):
    if request.method == "GET":
        current_user = get_user(request).username
        data = view_in_cart(request)[current_user]  # TODO Вызвать ответственную за это действие функцию
        r_format = request.GET.get('format')
        if not r_format:
            products = []
            for product_id, quantity in data['products'].items():
                product = DATABASE[product_id]
                product["quantity"] = quantity
                product["price_total"] = f"{quantity * product['price_after']:.2f}"
                products.append(product)
            return render(request, "store/cart.html", context={"products": products})
        if r_format.lower() == 'json':
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                         'indent': 4})

@login_required(login_url='login:login_view')
def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product)  # TODO Вызвать ответственную за это действие функцию
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product), remove_from_cart(request, id_product)
  # TODO Вызвать ответственную за это действие функцию
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def coupon_check_view(request, name_coupon):
    DATA_COUPON = {
        "coupon": {
            "discount": 10,
            "is_valid": True},
        "coupon_old": {
            "discount": 20,
            "is_valid": False},
    }
    if request.method == "GET":
        if DATA_COUPON.get(name_coupon):
            return JsonResponse(DATA_COUPON.get(name_coupon),
                                json_dumps_params={'ensure_ascii': False})
        return HttpResponseNotFound("Неверный купон")


def delivery_estimate_view(request):
    # База данных по стоимости доставки. Ключ - Страна; Значение словарь с городами и ценами; Значение с ключом fix_price
    # применяется если нет города в данной стране
    DATA_PRICE = {
        "Россия": {
            "Москва": {"price": 80},
            "Санкт-Петербург": {"price": 80},
            "fix_price": {"price": 100},
        },
    }
    if request.method == "GET":
        data = request.GET
        country = data.get('country')
        city = data.get('city')
        if DATA_PRICE.get(country):
            db_country = DATA_PRICE.get(country)
            return JsonResponse(db_country.get(city, db_country.get('fix_price')),
                                json_dumps_params={'ensure_ascii': False})
        return HttpResponseNotFound("Неверные данные")

@login_required(login_url='login:login_view')
def cart_buy_now_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product)
        if result:
            return redirect("store:cart_view")

        return HttpResponseNotFound("Неудачное добавление в корзину")


def cart_remove_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(request, id_product)  # TODO Вызвать функцию удаления из корзины
        if result:
            return redirect("store:cart_view")  # TODO Вернуть перенаправление на корзину

        return HttpResponseNotFound("Неудачное удаление из корзины")


