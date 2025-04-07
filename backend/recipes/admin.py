from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
)


class IngredientInRecipeInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount')
    extra = 1
    min_num = 1
    max_num = 100


@admin.register(Recipe)
class RecipePanel(admin.ModelAdmin):
    list_display = ('title', 'author', 'cook_time', 'count_favs')
    search_fields = ('title', 'author__username')
    inlines = [IngredientInRecipeInline]

    @admin.display(description="Сколько раз в избранном")
    def count_favs(self, obj):
        return obj.favorites.count()

    def title(self, obj):
        return obj.name

    def cook_time(self, obj):
        return obj.cooking_time


@admin.register(Ingredient)
class IngredientPanel(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoritePanel(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(RecipeIngredient)
class IngredientAmountPanel(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(ShoppingCart)
class CartPanel(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
