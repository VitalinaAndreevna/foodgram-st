from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.timezone import now

from foodgram.constants import (
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT,
    MAX_LENGTH_RECIPE_NAME,
    MIN_AMOUNT_VALUE,
    MIN_COOKING_TIME_VALUE,
)
from recipes.abstractions import UserRecipe

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        unique=True,
        verbose_name='Название ингредиента'
    )
    unit = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'unit'],
                name='unique_ingredient_combination')
        ]

    def __str__(self):
        return f"{self.title} ({self.unit})"


class Recipe(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_recipes',
        verbose_name='Автор рецепта'
    )
    title = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение'
    )
    description = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Используемые ингредиенты'
    )
    time_minutes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME_VALUE)],
        verbose_name='Время приготовления (в минутах)'
    )
    created_at = models.DateTimeField(default=now, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_links',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_links',
        verbose_name='Ингредиент'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT_VALUE)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Связь ингредиента с рецептом'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient_pair')
        ]

    def __str__(self):
        return f"{self.ingredient} — {self.quantity}"


class Favorite(UserRecipe):
    class Meta(UserRecipe.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'user_favorites'

    def __str__(self):
        return f"{self.user} → избранный рецепт → {self.recipe}"


class ShoppingCart(UserRecipe):
    class Meta(UserRecipe.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        default_related_name = 'user_carts'

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в корзину"
