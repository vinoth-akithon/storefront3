from django.http import HttpResponse
from django.shortcuts import render

def calculate():
    x = 1
    return x

# Create your views here.
def index(request):
    calculate()
    return render(request, "index.html")


def say_hello(request):
    return HttpResponse({"name": "vinoth"})
