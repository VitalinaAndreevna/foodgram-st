from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import MAX_LENGTH_USER_FIRST_NAME, MAX_LENGTH_USER_LAST_NAME


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    first_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIRST_NAME,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_USER_LAST_NAME,
        verbose_name='Фамилия пользователя'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        error_messages={
            'unique': 'Аккаунт с таким email уже зарегистрирован.',
        }
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Изображение профиля'
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'

    def __str__(self):
        return f'{self.username}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        related_name='subscribed_to',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Автор рецептов'
    )

    class Meta:
        ordering = ['subscriber']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} → {self.author}'
