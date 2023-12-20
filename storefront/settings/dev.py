import os
import dj_database_url
from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-y+=vy3%+!i@0%^j*8^mj1ss9o=%w9tb5(s^vq4ikt3b)+^-yup'

DATABASES = {
    'default': dj_database_url.config(
        default="mysql://root:Success.2023@localhost:3306/storefront3"
    )
}

CELERY_BROKER_URL = "redis://localhost:6379/1"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # database 1 allocated for message broker
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
