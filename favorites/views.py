from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from .models import Favorite
from products.models import Product


def show_favorites(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).order_by("-date")
        return render(request, "favorites/show_favorites.html", {"favorites": favorites})
    else:
        return redirect("users:user_login")


def user_favorites_add(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            ancient_product_code = request.POST.get('old_product_code')
            new_product_code = request.POST.get('new_product_code')

            ancient_product = Product.objects.get(code=ancient_product_code)
            new_product = Product.objects.get(code=new_product_code)

            Favorite.objects.get_or_create(ancient_product=ancient_product,
                                           new_product=new_product,
                                           user=request.user)

    return JsonResponse({"key": "value"})


def user_favorites_delete(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            ancient_product_code = request.POST.get('old_product_code')
            new_product_code = request.POST.get('new_product_code')

            ancient_product = Product.objects.get(code=ancient_product_code)
            new_product = Product.objects.get(code=new_product_code)

            try:
                Favorite.objects.get(user=request.user, ancient_product=ancient_product,
                                     new_product=new_product).delete()
            except Favorite.DoesNotExist:
                pass

    return JsonResponse({"key": "value"})
