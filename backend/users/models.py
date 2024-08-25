from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validator import username_validator


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Данный адрес уже используется'
        }
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует'
        },
        validators=[username_validator]
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    avatar = models.ImageField(
        verbose_name='Аватар',
        default=None,
        null=True
    )

    class Meta(AbstractUser.Meta):
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
