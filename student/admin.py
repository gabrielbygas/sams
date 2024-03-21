from django.contrib import admin
from .models import Appointment, Enquiry

# Register your models here.
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "date_appointment", "student", "service", "doctor", "time_schedule", "created_at")
    list_editable = ("date_appointment", "student", "service", "doctor", "time_schedule", )
    list_display_links = ("id", )
    search_fields = ("student", )
    list_filter = ("date_appointment", "time_schedule", )

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "doctor", "question", "answer", "is_answering", "created_at")
    list_editable = ("student", "doctor", "question", "answer", )
    list_display_links = ("id", "created_at", )
    search_fields = ("student", )
    list_filter = ("is_answering", )