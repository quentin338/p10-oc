from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from .forms import SearchForm
from .models import Product, Category
from favorites.models import Favorite


def index(request):
    form = SearchForm(request.GET or None)

    return render(request, "products/index.html", {"form": form})


def product_autocomplete(request):
    user_search = request.GET.get('term')

    if user_search is not None:
        results = Product.objects.search_autocomplete(user_search)

        return JsonResponse(results, safe=False)


def product_search(request):
    form = SearchForm(request.GET or None)

    if form.is_valid():
        user_search = form.cleaned_data["search"]
        old_product = Product.objects.get_old_product(user_search)

        if old_product is None:
            messages.add_message(request, messages.INFO, f"Désolé ! Nous n'avons rien trouvé pour remplacer {user_search}.")
            return redirect("products:index")

        better_products = Product.objects.get_better_products(old_product)

        if request.user.is_authenticated:
            for product in better_products:
                product.is_favorite = Favorite.objects\
                                      .is_favorite(request.user, old_product,
                                                   new_product=product)

        return render(request, "products/results.html", {"better_products": better_products,
                                                         "user_search": user_search,
                                                         "old_product": old_product}
                      )

    return redirect("products:index")


def details(request, product_id):
    try:
        product = Product.objects.get(code=product_id)
    except ObjectDoesNotExist:
        return redirect("products:index")

    return render(request, "products/details.html", {'product': product})
