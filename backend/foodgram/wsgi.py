import os

from django.core.wsgi import get_wsgi_application

# 📦 Установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

# 🚀 Получение WSGI-приложения
application = get_wsgi_application()
