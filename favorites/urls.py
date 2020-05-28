from django.urls import path
from . import views


app_name = "favorites"

urlpatterns = [
    path('add/', views.user_favorites_add, name="user_favorites_add"),
    path('delete/', views.user_favorites_delete, name="user_favorites_delete"),
    path('show/', views.show_favorites, name="show_favorites"),
]
