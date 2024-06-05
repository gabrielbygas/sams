from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from student.models import Appointment, Enquiry
from student.forms import AppointmentForm, EnquiryForm
from account.models import Student


# Create your views here.
@login_required
def home(request):
    context = {}
    context['user'] = request.user
    return render(request, "student/home.html", context)

# if you are not a doctor
def is_not_doctor(user):
    return not user.is_doctor()

@login_required
def student_error_page(request):
    context = {}
    if not request.user.is_superuser or request.user.is_doctor():
        context['error_message'] = "Doctor is not allowed to access this page."
    return render(request, "student/student_error_page.html", context)

# List Appointment
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_doctor, login_url='students:error-page'), name='dispatch')
class AppointmentListView(ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "student/appointment_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_student(): #if student
            student = Student.objects.get(user=user)
            return Appointment.objects.filter(student=student).order_by('-date_appointment')
        else: #if receptionist
            return Appointment.objects.all().order_by('-date_appointment')
        
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': #to specify an ajax request (copilot-Microsoft help)
            data = list(self.get_queryset().values(
                'id',
                'date_appointment', 
                'student__user__first_name',
                'student__user__last_name', 
                'service__name', 
                'doctor__user__first_name', 
                'doctor__user__last_name',
                'time_schedule'
            ))
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)


# Detail Appointment
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_doctor, login_url='students:error-page'), name='dispatch')
class AppointmentDetailView(DetailView):
    model = Appointment
    context_object_name = "appointment"
    template_name = "student/appointment_detail.html"

# Create Appointment
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_doctor, login_url='students:error-page'), name='dispatch')
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
        messages.success(self.request, 'Appointment created successfully!')
        return reverse("students:home")

# Update Appointment
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_doctor, login_url='students:error-page'), name='dispatch')
class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "student/appointment_update.html"

    def get_success_url(self):
        messages.success(self.request, 'Appointment updated successfully!')
        return reverse("students:update-appointment", args=[self.object.pk])

# Delete Appointment
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_doctor, login_url='students:error-page'), name='dispatch')
class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = "student/appointment_confirm_delete.html"
    context_object_name = "appointment"
    
    def get_success_url(self):
        messages.success(self.request, 'Appointment deleted successfully!')
        return reverse("students:list-appointment")
    
# List Enquiry
@method_decorator(login_required, name='dispatch')
class EnquiryListView(ListView):
    model = Enquiry
    context_object_name = "enquirys"
    template_name = "student/enquiry_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_student(): #if student
            student = Student.objects.get(user=user)
            return Enquiry.objects.filter(student=student).order_by('created_at')
        else: #if receptionist
            return Enquiry.objects.all().order_by('created_at')
        
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': #to specify an ajax request (copilot-Microsoft help)
            data = list(self.get_queryset().values(
                'id', 
                'student__user__first_name',
                'student__user__last_name', 
                'question',
                'answer', 
                'doctor__user__first_name', 
                'doctor__user__last_name',
                'is_answering',
                'created_at'
            ))
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)
        
# Detail Enquiry
@method_decorator(login_required, name='dispatch')
class EnquiryDetailView(DetailView):
    model = Enquiry
    context_object_name = "enquiry"
    template_name = "student/enquiry_detail.html"

# Create Enquiry
@method_decorator(login_required, name='dispatch')
class EnquiryCreateView(CreateView):
    model = Enquiry
    form_class = EnquiryForm
    template_name = "student/enquiry_create.html"

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'student'): #if user is student
            form.instance.student = user.student
        else: # if user is not student
            form.instance.student = form.cleaned_data.get('student')
        return super().form_valid(form)

    
    def get_success_url(self):
        messages.success(self.request, 'Enquiry created successfully!')
        return reverse("students:home")
    
# Update Enquiry
@method_decorator(login_required, name='dispatch')
class EnquiryUpdateView(UpdateView):
    model = Enquiry
    form_class = EnquiryForm
    template_name = "student/enquiry_update.html"

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'student'): #if user is student
            form.instance.student = user.student
        else: # if user is not student
            form.instance.student = form.cleaned_data.get('student')
        return super().form_valid(form)

    
    def get_success_url(self):
        messages.success(self.request, 'Enquiry created successfully!')
        return reverse("students:home")


# Enquiry Delete
@method_decorator(login_required, name='dispatch')
class EnquiryDeleteView(DeleteView):
    model = Enquiry
    template_name = "student/enquiry_confirm_delete.html"
    context_object_name = "enquiry"
    
    def get_success_url(self):
        messages.success(self.request, 'Enquiry deleted successfully!')
        return reverse("students:list-appointment")