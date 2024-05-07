from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .models import Appointment, Enquiry
from .forms import AppointmentForm


# Create your views here.
@login_required
def home(request):
    context = {}
    context['user'] = request.user
    return render(request, "student/home.html", context)


# List Appointment
class AppointmentListView(ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "student/appointment_list.html"

# Detail Appointment
class AppointmentDetailView(DetailView):
    model = Appointment
    context_object_name = "appointment"
    template_name = "student/appointment_detail.html"

# Create Appointment
class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    #context_object_name = "appointments"
    template_name = "student/appointment_create.html"

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'student'): #if user is student
            form.instance.student = user.student
        elif hasattr(user, 'receptionist'): # if user is receptionist
            form.instance.student = form.cleaned_data.get('student')
        return super().form_valid(form)

    
    def get_success_url(self):
        return reverse("student:home")

# Update Appointment
class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "student/appointment_update.html"

    def get_success_url(self):
        return reverse("student:home")

# Delete Appointment
class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = "student/appointment_confirm_delete.html"

    def get_success_url(self):
        return reverse("student:home")