from rest_framework import serializers


class UserRecipeRelationSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для моделей типа 'избранное' и 'корзина'."""

    class Meta:
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = attrs.get('user')
        recipe = attrs.get('recipe')

        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f"Этот рецепт уже добавлен в {self.Meta.model._meta.verbose_name}."
            )
        return attrs

    def to_representation(self, instance):
        from api.serializers import ShortRecipeSerializer
        return ShortRecipeSerializer(instance.recipe).data
