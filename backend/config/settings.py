# python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-f7de49fn+rw3vru7czz1z7^__)@bz0x2xg@-yqzhlquo#pr1-t'
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "channels",
    "django_filters",
    "apps.data_import",
    "apps.data_overview",
    "apps.data_annotation",
    "apps.data_export",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'apps.data_import.exceptions.ApiExceptionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
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
}]

ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = 'config.wsgi.application'

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Redis DB 划分：channels=0, celery(broker)=1, celery(result)=2, cache=3(可配)
REDIS_CACHE_DB = int(os.getenv("REDIS_CACHE_DB", "3"))

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(REDIS_HOST, REDIS_PORT, 0)]},  # 显式指定 DB=0
    }
}

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/2"
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 280

# Django 缓存：Redis（内置 RedisCache 后端）
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "TIMEOUT": None,
        "KEY_PREFIX": os.getenv("CACHE_KEY_PREFIX", "app"),
        # 不要添加 OPTIONS.client_class / CLIENT_CLASS 等第三方参数
        # 可选的 redis‑py 参数（如需）示例：
        # "OPTIONS": {
        #     "socket_connect_timeout": 2,
        #     "socket_timeout": 2,
        # }
    }
}

# 业务缓存 TTL 配置（秒）
APP_CACHE_TTLS = {
    "STATS_GLOBAL_TTL": int(os.getenv("STATS_GLOBAL_TTL", "60")),
    "RECENT_CORPUS_TTL": int(os.getenv("RECENT_CORPUS_TTL", "60")),
    "SEARCH_TTL": int(os.getenv("SEARCH_TTL", "300")),
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "0") == "1"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 63072000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

_csrf_hosts = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if _csrf_hosts:
    CSRF_TRUSTED_ORIGINS = [h if h.startswith("http") else f"https://{h}" for h in _csrf_hosts.split(",")]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "apps.data_import.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter"
    ],
    "EXCEPTION_HANDLER": "apps.data_import.exceptions.drf_exception_handler"
}

# === WebSocket / WS 协议与鉴权可调参数 ===
WS_SHARED_TOKEN = os.getenv("WS_SHARED_TOKEN", "")
WS_TOKEN_MAX_AGE = int(os.getenv("WS_TOKEN_MAX_AGE", "86400"))
WS_MAX_SEND_PER_SEC = int(os.getenv("WS_MAX_SEND_PER_SEC", "25"))
WS_NAMESPACE = os.getenv("WS_NAMESPACE", "public")
