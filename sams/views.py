from django.shortcuts import render


def home(request):
    return render(request, "sams/index.html")