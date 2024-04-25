from django.contrib import admin
from .models import CustomUser, Doctor, Student, Receptionist

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name", "dob", "phone", "photo", "sex", "created_at")
    list_editable = ("email", "first_name", "last_name", "dob", "phone", "photo", "sex",)
    list_display_links = ("id", "created_at", )
    search_fields = ("email", "first_name", "last_name", )
    list_filter = ("sex", )
    #list_per_page = 25  # On affiche 25 instances par page

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "doctorNumber", "get_full_name", "get_email", "user", "get_service")
    list_editable = ("doctorNumber", )
    list_display_links = ("id", )
    search_fields = ("doctorNumber", )
    list_filter = ("service", )

    def get_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name  # Access the first name of the user associated with the doctor
    get_full_name.short_description = 'Full Name'  # Display name for the field

    def get_email(self, obj):
        return obj.user.email  # Access the email of the user associated with the doctor
    get_email.short_description = 'Email'  # Display name for the field

    def get_service(self, obj):
        return obj.service.name
    get_service.short_descrition = 'Service'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "studentNumber", "get_full_name", "get_email", "user")
    list_editable = ("studentNumber", )
    list_display_links = ("id", )
    search_fields = ("studentNumber", )

    def get_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name 
    get_full_name.short_description = 'Full Name' 

    def get_email(self, obj):
        return obj.user.email  
    get_email.short_description = 'Email' 


@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    list_display = ("id", "receptionistNumber", "get_full_name", "get_email", "user")
    list_editable = ("receptionistNumber", )
    list_display_links = ("id", )
    search_fields = ("receptionistNumber", )

    def get_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name 
    get_full_name.short_description = 'Full Name' 

    def get_email(self, obj):
        return obj.user.email  
    get_email.short_description = 'Email'
