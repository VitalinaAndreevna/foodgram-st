from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для редактирования ингредиентов рецепта."""
    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ('ingredient', 'amount')
    autocomplete_fields = ['ingredient']  # Добавлен поиск по ингредиентам


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административная панель для рецептов."""
    list_display = ('name', 'author', 'cooking_time', 'favorites_count', 'pub_date')
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username', 'author__email')
    readonly_fields = ('pub_date',)
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)  # Если используется поле tags
    date_hierarchy = 'pub_date'  # Навигация по датам

    fieldsets = (
        (None, {
            'fields': ('author', 'name', 'image', 'text')
        }),
        ('Детали', {
            'fields': ('cooking_time', 'tags', 'pub_date')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorites')
        )

    @admin.display(description="В избранном", ordering='favorites_count')
    def favorites_count(self, obj):
        return obj.favorites_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административная панель для ингредиентов."""
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipe_usages')
        )

    @admin.display(description="Используется в рецептах", ordering='recipe_count')
    def recipe_count(self, obj):
        return obj.recipe_count


class UserRecipeAdmin(admin.ModelAdmin):
    """Базовый класс для избранного и корзины."""
    list_display = ('user', 'recipe_link', 'added_date')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    date_hierarchy = 'added_date'
    raw_id_fields = ('user', 'recipe')

    @admin.display(description="Рецепт")
    def recipe_link(self, obj):
        return format_html(
            '<a href="/admin/recipes/recipe/{}/change/">{}</a>',
            obj.recipe.id,
            obj.recipe.name
        )


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeAdmin):
    """Административная панель для избранного."""
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeAdmin):
    """Административная панель для корзины покупок."""
    pass


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Административная панель для связи рецептов и ингредиентов."""
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ['recipe', 'ingredient']
    