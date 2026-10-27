from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, UpdateView

from account.models import CustomUser, Doctor
from student.forms import EnquiryForm
from student.models import Appointment, Enquiry


# Create your views here.
@login_required
def home(request):
    user = request.user
    return render(request, "doctor/home.html", {"user": user})


@login_required
def get_doctors(request):
    service_id = request.GET.get("service")
    doctors = Doctor.objects.filter(service__id=service_id).order_by("service__name")
    return HttpResponse(
        '<option value="">---------</option>'
        + "".join(
            [
                f'<option value="{doctor.id}">{doctor.user.first_name} {doctor.user.last_name} | {doctor.doctorNumber}</option>'
                for doctor in doctors
            ]
        )
    )


# doctor/views.py — médecins et réception
def can_access_doctor_space(user):
    return user.has_role(CustomUser.Role.DOCTOR, CustomUser.Role.RECEPTIONIST)


@login_required
def doctor_error_page(request):
    context = {"error_message": "Only doctors and receptionists can access this page."}
    return render(request, "doctor/doctor_error_page.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    user_passes_test(can_access_doctor_space, login_url="doctors:error-page"), name="dispatch"
)
class EnquiryListView(ListView):
    model = Enquiry
    context_object_name = "enquirys"
    template_name = "doctor/enquiry_list.html"

    def get_queryset(self):
        return Enquiry.objects.filter(is_answering=False).order_by("-created_at")

    def render_to_response(self, context, **response_kwargs):
        if (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):  # to specify an ajax request (copilot-Microsoft help)
            data = list(
                self.get_queryset().values(
                    "id",
                    "student__user__first_name",
                    "student__user__last_name",
                    "question",
                    "answer",
                    "doctor__user__first_name",
                    "doctor__user__last_name",
                    "is_answering",
                    "created_at",
                )
            )
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    user_passes_test(can_access_doctor_space, login_url="doctors:error-page"), name="dispatch"
)
class EnquiryListAllView(ListView):
    model = Enquiry
    context_object_name = "enquirys"
    template_name = "doctor/enquiry_all_list.html"

    def get_queryset(self):
        return Enquiry.objects.all().order_by("-created_at")

    def render_to_response(self, context, **response_kwargs):
        if (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):  # to specify an ajax request (copilot-Microsoft help)
            data = list(
                self.get_queryset().values(
                    "id",
                    "student__user__first_name",
                    "student__user__last_name",
                    "question",
                    "answer",
                    "doctor__user__first_name",
                    "doctor__user__last_name",
                    "is_answering",
                    "created_at",
                )
            )
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    user_passes_test(can_access_doctor_space, login_url="doctors:error-page"), name="dispatch"
)
class EnquiryUpdateView(UpdateView):
    model = Enquiry
    form_class = EnquiryForm
    template_name = "doctor/enquiry_update.html"

    def form_valid(self, form):
        form.instance.is_answering = True
        user = self.request.user
        if hasattr(user, "student"):  # if user is student
            form.instance.student = user.student
        else:  # if user is not student
            form.instance.student = form.cleaned_data.get("student")
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Enquiry created successfully!")
        return reverse("doctors:list-enquiry")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    user_passes_test(can_access_doctor_space, login_url="doctors:error-page"), name="dispatch"
)
class EnquiryDetailView(DetailView):
    model = Enquiry
    context_object_name = "enquiry"
    template_name = "doctor/enquiry_detail.html"


@method_decorator(login_required, name="dispatch")
@method_decorator(
    user_passes_test(can_access_doctor_space, login_url="doctors:error-page"), name="dispatch"
)
class AppointmentListView(ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "doctor/appointment_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor():  # if doctor
            doctor = Doctor.objects.get(user=user)
            return Appointment.objects.filter(doctor=doctor).order_by("-date_appointment")
        else:  # if receptionist
            return Appointment.objects.all().order_by("-date_appointment")

    def render_to_response(self, context, **response_kwargs):
        if (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):  # to specify an ajax request (copilot-Microsoft help)
            data = list(
                self.get_queryset().values(
                    "id",
                    "date_appointment",
                    "student__user__first_name",
                    "student__user__last_name",
                    "service__name",
                    "doctor__user__first_name",
                    "doctor__user__last_name",
                    "time_schedule",
                )
            )
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    user_passes_test(can_access_doctor_space, login_url="doctors:error-page"), name="dispatch"
)
class AppointmentDetailView(DetailView):
    model = Appointment
    context_object_name = "appointment"
    template_name = "doctor/appointment_detail.html"
