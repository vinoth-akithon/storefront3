import os
import dj_database_url
from .common import *


DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = [os.getenv("ALLOWED_HOST")]


DATABASES = {
    'default': dj_database_url.config()
}


REDIS_URL = os.getenv("REDIS_URL")

CELERY_BROKER_URL = REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
