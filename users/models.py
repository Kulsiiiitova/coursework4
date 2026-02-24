from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.CharField(unique=True, verbose_name="email")
    username = models.CharField(blank=True, null=True, verbose_name="name")
    comment = models.CharField(blank=True, null=True, verbose_name="comment")
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Mailing recipient'
        verbose_name_plural = 'Mailing recipients'
        permissions = [
            ('view_all_users', 'Может просматривать всех пользователей'),
            ('block_user', 'Может блокировать пользователей'),
        ]

    def __str__(self):
        return self.email