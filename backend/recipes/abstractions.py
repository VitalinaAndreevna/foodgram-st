from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class UserRecipe(models.Model):
    """Абстрактная модель для связи пользователей и рецептов."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='%(class)s_recipes'  # Динамическое имя связи
    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='%(class)s_users'  # Динамическое имя связи
    )
    added_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['-added_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s'
            )
        ]

    def __str__(self):
        return f'{self.user.username} → {self.recipe.name}'
    