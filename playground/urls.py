from django.urls import path
from . import views

# url configuration
urlpatterns = [
    path("index/", views.index),
    path("hello/", views.say_hello)
]