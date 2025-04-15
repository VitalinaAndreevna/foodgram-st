from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.abstractions.serializers import BaseUserRecipeSerializer
from api.fields import Base64ImageField
from foodgram.constants import MIN_COOKING_TIME_VALUE
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart
from users.models import Follow

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed', 'avatar')
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на этого автора."""
        request = self.context.get('request')
        return (
            request and
            request.user.is_authenticated and
            obj.follower.filter(user=request.user).exists()
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeBaseMixin:
    """Общие методы для сериализаторов рецептов."""
    
    def get_user_relation_status(self, obj, relation_model):
        """Проверяет отношение пользователя к рецепту."""
        request = self.context.get('request')
        return (
            request and
            request.user.is_authenticated and
            relation_model.objects.filter(user=request.user, recipe=obj).exists()
        )


class RecipeReadSerializer(RecipeBaseMixin, serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        return self.get_user_relation_status(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_user_relation_status(obj, ShoppingCart)

    def get_ingredients(self, obj):
        """Получает список ингредиентов с количествами."""
        return [
            {
                **IngredientSerializer(ri.ingredient).data,
                'amount': ri.amount
            }
            for ri in obj.recipe_ingredients.all()
        ]


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['name', 'image', 'text', 'ingredients', 'cooking_time']

    def validate_cooking_time(self, value):
        """Проверяет минимальное время готовки."""
        if value < MIN_COOKING_TIME_VALUE:
            raise ValidationError({
                "cooking_time": [
                    f"Время готовки не может быть меньше {MIN_COOKING_TIME_VALUE} мин."
                ]
            })
        return value

    def validate_ingredients(self, ingredients):
        """Валидация списка ингредиентов."""
        if not ingredients:
            raise ValidationError({"ingredients": ["Список ингредиентов не может быть пустым."]})

        ingredient_ids = [item['id'] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError({"ingredients": ["Ингредиенты не должны повторяться."]})

        return ingredients

    def create_ingredients(self, recipe, ingredients_data):
        """Создает связи рецепта с ингредиентами."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in ingredients_data
        ])

    def create(self, validated_data):
        """Создает рецепт с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт и его ингредиенты."""
        ingredients_data = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает данные в формате RecipeReadSerializer."""
        return RecipeReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['recipes', 'recipes_count']

    def get_recipes(self, obj):
        """Получает список рецептов с возможностью ограничения количества."""
        request = self.context.get('request')
        queryset = obj.recipes.all()
        
        if request:
            if limit := request.query_params.get('recipes_limit'):
                if limit.isdigit():
                    queryset = queryset[:int(limit)]
        
        return ShortRecipeSerializer(queryset, many=True, context=self.context).data


class SubscriptionSerializer(serializers.Serializer):
    following_id = serializers.IntegerField()

    def validate_following_id(self, value):
        """Проверяет валидность подписки."""
        user = self.context['request'].user
        following_user = get_object_or_404(User, pk=value)

        if following_user == user:
            raise ValidationError("Невозможно подписаться на себя")
        if Follow.objects.filter(user=user, following=following_user).exists():
            raise ValidationError("Вы уже подписаны на этого пользователя")

        return value

    def create(self, validated_data):
        """Создает подписку."""
        return Follow.objects.create(
            user=self.context['request'].user,
            following_id=validated_data['following_id']
        )

    def to_representation(self, instance):
        """Возвращает данные подписки."""
        return FollowSerializer(instance.following, context=self.context).data


class FavoriteSerializer(BaseUserRecipeSerializer):
    class Meta(BaseUserRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseUserRecipeSerializer):
    class Meta(BaseUserRecipeSerializer.Meta):
        model = ShoppingCart
        