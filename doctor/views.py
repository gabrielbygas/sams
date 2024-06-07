from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from account.models import Doctor, Student
from student.models import Appointment, Enquiry
from student.forms import AppointmentForm, EnquiryForm
from django.views.generic import ListView, UpdateView, DetailView
from django.http import JsonResponse

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

# if you are not a student
def is_not_student(user):
    return not user.is_student()

@login_required
def doctor_error_page(request):
    context = {}
    if not request.user.is_superuser or request.user.is_student():
        context['error_message'] = "Student is not allowed to access this page."
    return render(request, "student/doctor_error_page.html", context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_student, login_url='doctors:error-page'), name='dispatch')
class EnquiryListView(ListView):
    model = Enquiry
    context_object_name = "enquirys"
    template_name = "doctor/enquiry_list.html"

    def get_queryset(self):
        return Enquiry.objects.filter(is_answering=False).order_by('created_at')

        
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

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_student, login_url='doctors:error-page'), name='dispatch')
class EnquiryListAnsweredView(ListView):
    model = Enquiry
    context_object_name = "enquirys"
    template_name = "doctor/enquiry_answered_list.html"

    def get_queryset(self):
        return Enquiry.objects.filter(is_answering=False).order_by('created_at')

        
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
        
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_not_student, login_url='doctors:error-page'), name='dispatch')
class EnquiryUpdateView(UpdateView):
    model = Enquiry
    form_class = EnquiryForm
    template_name = "doctor/enquiry_update.html"

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'student'): #if user is student
            form.instance.student = user.student
        else: # if user is not student
            form.instance.student = form.cleaned_data.get('student')
        return super().form_valid(form)

    
    def get_success_url(self):
        messages.success(self.request, 'Enquiry created successfully!')
        return reverse("doctors:list-enquiry")