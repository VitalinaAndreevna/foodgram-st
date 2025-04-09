from django.urls import path

from api import views as viewset_module

redirect_patterns = [
    path(
        '<str:short_code>/',
        viewset_module.RecipeViewSet.as_view({'get': 'redirect_to_recipe'}),
        name='recipe-redirect'
    ),
]
