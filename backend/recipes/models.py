from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from foodgram.constants import (
    MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT,
    MAX_LENGTH_INGREDIENT_NAME,
    MIN_AMOUNT_VALUE,
    MAX_LENGTH_RECIPE_NAME, 
    MIN_COOKING_TIME_VALUE
)
from recipes.abstractions import UserRecipe

class Ingredient(models.Model):
    """Модель ингредиента с уникальным названием и единицей измерения."""
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        unique=True,
        db_index=True  # Добавлен индекс для ускорения поиска
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_pair'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента с указанием количества."""
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.PROTECT,  # Защита от удаления используемого ингредиента
        related_name='recipe_usages'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_AMOUNT_VALUE)]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количества ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_per_recipe'
            )
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient.measurement_unit} {self.ingredient.name}'


class Recipe(models.Model):
    """Модель рецепта с ингредиентами, временем приготовления и изображением."""
    author = models.ForeignKey(
        'users.User',
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='authored_recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_RECIPE_NAME,
        db_index=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/%Y/%m/%d/',  # Более структурированное хранение
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (минуты)',
        validators=[MinValueValidator(MIN_COOKING_TIME_VALUE)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,  # Более точное название для автоматического заполнения
        db_index=True
    )
    # tags = models.ManyToManyField(  # Добавлено поле тегов, если используется
    #     'Tag',
    #     related_name='recipes',
    #     blank=True,
    #     verbose_name='Теги'
    # )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        indexes = [
            models.Index(fields=['name'], name='recipe_name_idx')
        ]

    def __str__(self):
        return f'{self.name} (автор: {self.author.username})'


class Favorite(UserRecipe):
    """Модель для хранения избранных рецептов пользователей."""
    
    class Meta(UserRecipe.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.user.username} → {self.recipe.name}'


class ShoppingCart(UserRecipe):
    """Модель корзины покупок пользователя."""
    
    class Meta(UserRecipe.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        default_related_name = 'shopping_carts'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name} в корзине'
    