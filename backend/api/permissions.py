from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешает:
    - Чтение всем (SAFE_METHODS)
    - Запись только автору объекта
    """
    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        """Глобальная проверка доступа."""
        return True

    def has_object_permission(self, request, view, obj):
        """Проверка прав для конкретного объекта."""
        if request.method in self.SAFE_METHODS:
            return True
        return obj.author == request.user
    