import base64
import csv
import os
import uuid
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from fpdf import FPDF
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.abstractions.views import manage_user_recipe
from api.fields import Base64ImageField
from api.filters import RecipeFilter
from api.paginations import Pagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    UserSerializer
)
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart
from users.models import Follow

User = get_user_model()


class FileGenerationMixin:
    """Миксин для генерации файлов списка покупок."""

    @staticmethod
    def generate_txt_file(ingredients):
        content = "\n".join(
            f"{i['name']} ({i['measurement_unit']}) — {i['amount']}"
            for i in ingredients
        )
        response = HttpResponse(content, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response

    @staticmethod
    def generate_csv_file(ingredients):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
        writer.writerows(
            (i['name'], i['amount'], i['measurement_unit'])
            for i in ingredients
        )
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.csv"'
        return response

    @staticmethod
    def generate_pdf_file(ingredients):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Список покупок", ln=True, align='C')
        for ingredient in ingredients:
            pdf.cell(
                200, 10,
                txt=f"{ingredient['name']} ({ingredient['measurement_unit']}) — {ingredient['amount']}",
                ln=True
            )
        response = HttpResponse(
            pdf.output(dest='S').encode('latin1'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        return response


class AvatarHandlingMixin:
    """Миксин для обработки аватаров пользователей."""

    @staticmethod
    def process_avatar_upload(user, avatar_data):
        """Обрабатывает загрузку аватара в формате base64."""
        if user.avatar:
            user.avatar.delete()

        format, imgstr = avatar_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(
            base64.b64decode(imgstr),
            name=f"{uuid.uuid4()}.{ext}"
        )
        user.avatar.save(data.name, data, save=True)


class UserViewSet(DjoserUserViewSet, AvatarHandlingMixin):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    pagination_class = Pagination
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получение данных текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Управление аватаром пользователя."""
        user = request.user

        if request.method == 'PUT':
            if not (avatar_data := request.data.get('avatar')):
                return Response(
                    {"avatar": ["Это поле обязательно."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                self.process_avatar_upload(user, avatar_data)
                return Response(
                    {"avatar": request.build_absolute_uri(user.avatar.url)},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # DELETE
        if not user.avatar:
            return Response(
                {"detail": "Аватар отсутствует."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_subscriptions(self, request):
        """Получение списка подписок."""
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticated]
    )
    def manage_subscription(self, request, id=None):
        """Управление подпиской на пользователя."""
        user = request.user

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'following_id': id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            follow = serializer.save()
            return Response(
                FollowSerializer(
                    follow.following,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        following_user = get_object_or_404(User, pk=id)
        follow_instance = Follow.objects.filter(
            user=user,
            following=following_user
        ).first()

        if not follow_instance:
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet, FileGenerationMixin):
    queryset = Recipe.objects.all().select_related('author').prefetch_related('ingredients')
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def _get_ingredients_list(self, user):
        """Приватный метод для получения списка ингредиентов."""
        return (
            RecipeIngredient.objects
            .filter(recipe__shopping_carts__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[permissions.AllowAny]
    )
    def get_link(self, request, pk=None):
        """Генерация короткой ссылки на рецепт."""
        recipe = self.get_object()
        short_code = Base64ImageField.to_base62(recipe.id)
        short_link = request.build_absolute_uri(f"/s/{short_code}")
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    def redirect_to_recipe(self, request, short_code=None):
        """Редирект по короткой ссылке."""
        try:
            recipe_id = Base64ImageField.from_base62(short_code)
        except ValueError:
            return Response(
                {"detail": "Неверный короткий код."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe = get_object_or_404(Recipe, id=recipe_id)
        return redirect(request.build_absolute_uri(f"/recipes/{recipe.id}/"))

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в разных форматах."""
        FORMAT_HANDLERS = {
            'txt': self.generate_txt_file,
            'csv': self.generate_csv_file,
            'pdf': self.generate_pdf_file
        }

        ingredients = self._get_ingredients_list(request.user)
        file_format = request.query_params.get('format', 'txt').lower()

        if handler := FORMAT_HANDLERS.get(file_format):
            return handler(ingredients)
        return Response(
            {"detail": "Неверный формат файла"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def manage_shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из корзины."""
        return manage_user_recipe(
            request,
            pk,
            ShoppingCart,
            ShoppingCartSerializer
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def manage_favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        return manage_user_recipe(
            request,
            pk,
            Favorite,
            FavoriteSerializer
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ['name']
    pagination_class = None

    def get_queryset(self):
        """Фильтрация ингредиентов по имени."""
        queryset = super().get_queryset()
        if name := self.request.query_params.get('name'):
            queryset = queryset.filter(name__istartswith=name)
        return queryset
    