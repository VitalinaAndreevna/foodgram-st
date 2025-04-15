from django_filters import rest_framework as filters
from django_filters.filters import BooleanFilter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для рецептов с поддержкой:
    - Избранного
    - Корзины покупок
    - Фильтрации по автору
    """
    is_favorited = BooleanFilter(
        method='filter_by_user_relation',
        field_name='favorites'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_by_user_relation',
        field_name='shopping_carts'
    )

    class Meta:
        model = Recipe
        fields = ['author']

    def filter_by_user_relation(self, queryset, field_name, value):
        """
        Универсальный метод фильтрации по пользовательским отношениям.
        """
        if not value or not self.request.user.is_authenticated:
            return queryset
            
        lookup = f"{field_name}__user"
        return queryset.filter(**{lookup: self.request.user})
    