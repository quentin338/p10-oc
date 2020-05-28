from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path('', views.index, name="index"),
    path('new/', views.create_new_user, name="user_registration"),
    path('new/add/', views.add_new_user, name="user_add"),
    path('login/', views.user_login, name="user_login"),
    path('login/check/', views.user_check_login, name="user_check_login"),
    path('logout/', views.user_logout, name="user_logout"),
    path('account/', views.user_account, name="user_account"),
]
