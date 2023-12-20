from django.urls import path
from . import views

# url configuration
urlpatterns = [
    path("index/", views.Index.as_view()),
    path("hello/", views.say_hello)
]
