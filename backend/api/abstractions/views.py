from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def toggle_recipe_relation(request, recipe_id, relation_model, serializer_cls):
    recipe_instance = get_object_or_404(Recipe, pk=recipe_id)

    if request.method == 'POST':
        payload = {
            'user': request.user.id,
            'recipe': recipe_instance.id
        }
        serializer = serializer_cls(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    relation_object = relation_model.objects.filter(
        user=request.user, recipe=recipe_instance
    ).first()

    if relation_object is None:
        return Response(
            {"detail": f"Recipe not found in {relation_model._meta.verbose_name}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    relation_object.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
