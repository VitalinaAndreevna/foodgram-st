from django.urls import path

from api.views import RecipeViewSet

app_name = 'redirect'

urlpatterns = [
    path(
        '<str:short_code>/',
        RecipeViewSet.as_view({'get': 'redirect_to_recipe'}),
        name='recipe-redirect'
    ),
]
