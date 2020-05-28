from django.urls import path
from . import views


app_name = "products"

urlpatterns = [
    path('', views.index, name="index"),
    path('products/', views.product_search, name="product_search"),
    path('products/autocomplete/', views.product_autocomplete, name="product_autocomplete"),
    path('products/<int:product_id>', views.details, name="product_details"),
]
