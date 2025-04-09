from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe, Ingredient, Tag, Favorite, ShoppingCart
from users.models import Follow, User
from .permissions import IsAuthorOrReadOnly
from .paginations import CustomPaginator
from .serializers import (
    RecipeViewSerializer, RecipeCreateSerializer,
    IngredientSerializer, TagSerializer, FollowSerializer,
    UserSerializer
)


class RecipeHandler(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeViewSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._add_related_object(Favorite, request.user, pk)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        return self._remove_related_object(Favorite, request.user, pk)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cart(self, request, pk=None):
        return self._add_related_object(ShoppingCart, request.user, pk)

    @cart.mapping.delete
    def remove_cart(self, request, pk=None):
        return self._remove_related_object(ShoppingCart, request.user, pk)

    def _add_related_object(self, model, user, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response({'detail': 'Уже добавлено'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeViewSerializer(recipe, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_related_object(self, model, user, recipe_id):
        item = model.objects.filter(user=user, recipe__id=recipe_id)
        if item.exists():
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Не найдено'}, status=status.HTTP_400_BAD_REQUEST)


class IngredientHandler(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class TagHandler(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class FollowHandler(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        follows = Follow.objects.filter(user=request.user)
        paginated = CustomPaginator().paginate_queryset(follows, request)
        serializer = FollowSerializer(paginated, many=True, context={'request': request})
        return CustomPaginator().get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)
        if request.user == author:
            return Response({'detail': 'Нельзя подписаться на себя'}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = Follow.objects.get_or_create(user=request.user, following=author)
        if not created:
            return Response({'detail': 'Уже подписаны'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        relation = Follow.objects.filter(user=request.user, following__id=pk)
        if not relation.exists():
            return Response({'detail': 'Вы не подписаны на этого автора'}, status=status.HTTP_400_BAD_REQUEST)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
