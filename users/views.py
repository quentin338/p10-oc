from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.db.utils import IntegrityError

from .forms import UserForm
from .models import User
from products.forms import SearchForm


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse("users:user_account"))
    else:
        return redirect("users:user_registration")


def user_login(request):
    user_form = UserForm(request.GET or None)
    form = SearchForm(request.GET or None)
    return render(request, 'users/login.html', {'user_form': user_form, 'form': form})


def user_logout(request):
    logout(request)

    return redirect("products:index")


def user_check_login(request):
    form = UserForm(request.GET or None)

    if form.is_valid():
        user_mail = form.cleaned_data['email']
        user_password = form.cleaned_data['password']

        user = authenticate(email=user_mail, password=user_password)

        if user:
            login(request, user)
        else:
            messages.add_message(request, messages.INFO, "Nom d'utilisateur ou mot de passe "
                                                         "incorrect.")
            return redirect("users:user_login")

    return redirect(reverse("products:index"))


def create_new_user(request):
    user_form = UserForm(request.GET or None)
    form = SearchForm(request.GET or None)

    return render(request, "users/registration.html", {'form': form, 'user_form': user_form})


def add_new_user(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user_mail = form.cleaned_data['email']
        user_password = form.cleaned_data['password']

        try:
            user = User.objects.create_user(email=user_mail, password=user_password)
            return redirect("users:user_login")
        except IntegrityError as e:
            messages.add_message(request, messages.INFO, "Cet email a déjà un compte.")

    return redirect("users:user_registration")


def user_account(request):
    if request.user.is_authenticated:
        return render(request, "users/account.html")

    return redirect("users:user_login")
