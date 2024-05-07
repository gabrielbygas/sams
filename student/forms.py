from django import forms
from .models import Appointment, Enquiry
from account.models import CustomUser, Student, Receptionist, Doctor
from doctor.models import Service


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date_appointment', 'student', 'service', 'doctor', 'time_schedule']
        widgets = {
            'date_appointment': forms.DateInput(attrs={'class': 'form-control datepicker', 'required': True}),
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
                self.fields['doctor'].queryset = Doctor.objects.filter(service__id=service_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['doctor'].queryset = self.instance.service.doctor_set.order_by('name')
