from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    context = {}
    context['user'] = request.user
    return render(request, "student/home.html", context)
