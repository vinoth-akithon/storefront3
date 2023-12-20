from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-y+=vy3%+!i@0%^j*8^mj1ss9o=%w9tb5(s^vq4ikt3b)+^-yup'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Aki@1026'
    }
}
