import logging
import os
from datetime import timedelta
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-f7de49fn+rw3vru7czz1z7^__)@bz0x2xg@-yqzhlquo#pr1-t'
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    # Prometheus 需放在首部，确保中间件统计完整
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "channels",
    "django_filters",
    "apps.data_import",
    "apps.data_overview",
    "apps.data_annotation",
    "apps.data_export",
]

MIDDLEWARE = [
    # Prometheus Before
    "django_prometheus.middleware.PrometheusBeforeMiddleware",

    'django.middleware.security.SecurityMiddleware',
    # 请求 ID + 日志上下文
    'apps.data_import.middleware.RequestIdMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'apps.data_import.exceptions.ApiExceptionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Prometheus After
    "django_prometheus.middleware.PrometheusAfterMiddleware",
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

# Redis DB: channels=0, celery(broker)=1, celery(result)=2, cache=3
REDIS_CACHE_DB = int(os.getenv("REDIS_CACHE_DB", "3"))

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(REDIS_HOST, REDIS_PORT, 0)]},
    }
}

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/2"
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 280

# 使 Celery 复用 Django 的日志配置
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "TIMEOUT": None,
        "KEY_PREFIX": os.getenv("CACHE_KEY_PREFIX", "app"),
    }
}

APP_CACHE_TTLS = {
    "STATS_GLOBAL_TTL": int(os.getenv("STATS_GLOBAL_TTL", "60")),
    "RECENT_CORPUS_TTL": int(os.getenv("RECENT_CORPUS_TTL", "60")),
    "SEARCH_TTL": int(os.getenv("SEARCH_TTL", "300")),
}

DATABASES = {
    'default': {
        # 使用 django-prometheus 包装的后端，暴露 DB 指标
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'ner_db'),
        'USER': os.getenv('POSTGRES_USER', 'ner'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'hiboranez'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
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
    "EXCEPTION_HANDLER": "apps.data_import.exceptions.drf_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# WebSocket / WS
WS_SHARED_TOKEN = os.getenv("WS_SHARED_TOKEN", "")
WS_TOKEN_MAX_AGE = int(os.getenv("WS_TOKEN_MAX_AGE", "86400"))
WS_MAX_SEND_PER_SEC = int(os.getenv("WS_MAX_SEND_PER_SEC", "25"))
WS_NAMESPACE = os.getenv("WS_NAMESPACE", "public")

# SimpleJWT 配置
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ---------- 结构化 JSON 日志 ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_context": {
            "()": "apps.data_import.middleware.RequestContextFilter",
        }
    },
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(path)s %(method)s %(status_code)s %(user_id)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "json",
            "filters": ["request_context"],
        }
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    },
    "loggers": {
        "django.server": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "channels": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "celery": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    }
}

# ---------- Sentry ----------
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            LoggingIntegration(
                level=logging.INFO,  # 记录 INFO 以上到 breadcrumbs
                event_level=logging.ERROR  # ERROR 以上作为事件上报
            )
        ],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
        send_default_pii=True,
        environment=os.getenv("SENTRY_ENV", "dev"),
    )
