from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Follow

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Админ-панель для модели пользователя."""
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'followers_count',
        'followings_count'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _followers_count=Count('followers'),
            _followings_count=Count('followings')
        )

    @admin.display(ordering='_followers_count', description=_('Followers'))
    def followers_count(self, obj):
        return obj._followers_count

    @admin.display(ordering='_followings_count', description=_('Followings'))
    def followings_count(self, obj):
        return obj._followings_count


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-панель для подписок."""
    list_display = ('user', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'user__username',
        'user__email',
        'following__username',
        'following__email'
    )
    raw_id_fields = ('user', 'following')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'following')
    