"""
🔌 ASGI entry point for the Foodgram project.

This file exposes the ASGI callable as a module-level variable named `application`.
Used for asynchronous deployment (WebSockets, long polling, etc).
"""

import os

from django.core.asgi import get_asgi_application

# Устанавливаем модуль настроек по умолчанию
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

# Получаем ASGI-приложение
application = get_asgi_application()
