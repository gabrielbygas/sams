from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from account.models import Doctor

# Create your views here.
@login_required
def home(request):
    user = request.user
    return render(request, "doctor/home.html", {'user': user})

@login_required
def get_doctors(request):
    service_id = request.GET.get('service')
    doctors = Doctor.objects.filter(service__id=service_id).order_by('service__name')
    return HttpResponse('<option value="">---------</option>' + ''.join([f'<option value="{doctor.id}">{doctor.user.first_name} {doctor.user.last_name} | {doctor.doctorNumber}</option>' for doctor in doctors]))