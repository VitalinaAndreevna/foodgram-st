from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLinkedRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Связанный рецепт'
    )

    class Meta:
        abstract = True
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_pair_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} ↔ {self.recipe}'
