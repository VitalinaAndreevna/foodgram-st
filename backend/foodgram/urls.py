from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Основное API
    path('api/', include('api.urls')),

    # Специальные редиректы
    path('links/', include('api.transitions')),
]

# Медиа-файлы только при отладке
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
