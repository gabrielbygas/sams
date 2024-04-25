from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect


def home(request):
    return render(request, "sams/index.html")

def back(request):
    # Check if the HTTP_REFERER header is present
    if 'HTTP_REFERER' in request.META:
        # Redirect the user to the previous page
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        # If HTTP_REFERER is not present, redirect to a default URL
        return HttpResponseRedirect('/')