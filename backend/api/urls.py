from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet, IngredientViewSet,
    RecipeViewSet, SubscriptionViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}), name='subscribe'),
]
