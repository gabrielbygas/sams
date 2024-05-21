from django import forms
from student.models import Appointment, Enquiry
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser, Student, Receptionist, Doctor
from doctor.models import Service


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date_appointment', 'student', 'service', 'doctor', 'time_schedule']
        widgets = {
            'date_appointment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'student': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'service': forms.Select(attrs={'class': 'form-control', 'id': 'id_service', 'required': True}),
            'doctor': forms.Select(attrs={'class': 'form-control', 'id': 'id_doctor', 'required': True}),
            'time_schedule': forms.Select(choices=Appointment.TIME_SCHEDULES, attrs={'class': 'form-control', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.none()

        if 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                self.fields['doctor'].queryset = Doctor.objects.filter(service__id=service_id).order_by('user__first_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['doctor'].queryset = self.instance.service.doctor_set.order_by('user__first_name')

    #verify the contraint: a user should have only one appointment per day, before saving the form
    def clean(self):
        cleaned_data = super().clean()
        date_appointment = cleaned_data.get("date_appointment")
        student = cleaned_data.get("student")

        if Appointment.objects.filter(date_appointment=date_appointment, student=student).exists():
            raise ValidationError(_("You already have an appointment on this date."))
        
        return cleaned_data
