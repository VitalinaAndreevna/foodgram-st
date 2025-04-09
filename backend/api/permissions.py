from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Доступ только для автора объекта на изменения.
    Остальные могут только просматривать.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class IsProfileOwner(BasePermission):
    """
    Доступ к профилю только у владельца.
    """
    def has_permission(self, request, view):
        return view.kwargs.get('id') == str(request.user.id)
