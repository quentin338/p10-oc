from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
