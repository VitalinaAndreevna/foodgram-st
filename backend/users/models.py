from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram.constants import (
    MAX_LENGTH_USER_FIRST_NAME,
    MAX_LENGTH_USER_LAST_NAME,
    MAX_LENGTH_USER_USERNAME
)


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве идентификатора."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('Пользователь с таким email уже существует.'),
        }
    )
    username = models.CharField(
        _('username'),
        max_length=MAX_LENGTH_USER_USERNAME,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=MAX_LENGTH_USER_FIRST_NAME,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=MAX_LENGTH_USER_LAST_NAME,
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='users/avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_user_email'
            ),
            models.UniqueConstraint(
                fields=['username'],
                name='unique_user_username'
            )
        ]

    def __str__(self):
        return f'{self.username} ({self.email})'


class Follow(models.Model):
    """Модель подписки пользователей друг на друга."""
    user = models.ForeignKey(
        User,
        verbose_name=_('follower'),
        on_delete=models.CASCADE,
        related_name='followings'
    )
    following = models.ForeignKey(
        User,
        verbose_name=_('following'),
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('follow')
        verbose_name_plural = _('follows')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return _('%(user)s follows %(following)s') % {
            'user': self.user.username,
            'following': self.following.username
        }
    