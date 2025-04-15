from django.urls import include, path
from rest_framework import routers

from api import views as api_views

# Роутеры API
app_name = 'api'

# Роутер для пользователей
user_router = routers.DefaultRouter()
user_router.register(
    'users',
    api_views.UserViewSet,
    basename='users'
)

# Роутер для рецептов и ингредиентов
recipe_router = routers.DefaultRouter()
recipe_router.register(
    'recipes',
    api_views.RecipeViewSet,
    basename='recipes'
)
recipe_router.register(
    'ingredients',
    api_views.IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    # Авторизация
    path('auth/', include('djoser.urls.authtoken')),
    
    # API пользователей
    path('', include(user_router.urls)),
    
    # API рецептов и ингредиентов
    path('', include(recipe_router.urls)),
]
