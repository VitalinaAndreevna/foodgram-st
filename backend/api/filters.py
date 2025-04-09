from django_filters.rest_framework import FilterSet, CharFilter, BooleanFilter, NumberFilter, AllValuesMultipleFilter

from recipes.models import Recipe, Ingredient


class IngredientNameFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeParamsFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    author = NumberFilter(field_name='author__id')
    is_favorited = BooleanFilter(method='filter_favorites')
    is_in_shopping_cart = BooleanFilter(method='filter_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_favorites(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(cart__user=user)
        return queryset
