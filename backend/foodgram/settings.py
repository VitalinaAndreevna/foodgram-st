import os
from datetime import timedelta
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# 📌 Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Загрузка переменных окружения
load_dotenv()

# 💬 Безопасность
SECRET_KEY = os.getenv('APP_SECRET_KEY', get_random_secret_key())
DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('APP_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 🛠️ Конфигурация базы данных
USE_SQLITE = os.getenv('APP_USE_SQLITE', 'false').lower() == 'true'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('APP_DB_ENGINE'),
            'NAME': os.getenv('APP_DB_NAME'),
            'USER': os.getenv('APP_DB_USER'),
            'PASSWORD': os.getenv('APP_DB_PASSWORD'),
            'HOST': os.getenv('APP_DB_HOST'),
            'PORT': os.getenv('APP_DB_PORT'),
        }
    }

# 🔌 Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние библиотеки
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    # Локальные приложения
    'api',
    'users',
    'recipes',
]

# ⚙️ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 📍 Конфигурация путей
ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'


# 🔐 Аутентификация
AUTH_USER_MODEL = 'users.User'

# 🛠️ Настройки Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.paginations.CustomPagination',
    'PAGE_SIZE': 6,
}

# 🕒 JWT (если используется)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 🌍 Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 📁 Статика и медиа
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ✉️ Email (если используется)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
