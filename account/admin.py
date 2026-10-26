from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserAdminChangeForm, CustomUserAdminCreationForm
from .models import CustomUser, Doctor, Receptionist, Student


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "dob",
        "phone",
        "photo",
        "sex",
        "created_at",
    )
    list_display_links = (
        "id",
        "created_at",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "sex")
    ordering = ("email",)
    readonly_fields = ("last_login", "created_at")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "dob", "phone", "photo", "sex")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    # list_per_page = 25  # On affiche 25 instances par page


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "doctorNumber", "get_full_name", "get_email", "user", "get_service")
    list_editable = ("doctorNumber",)
    list_display_links = ("id",)
    search_fields = ("doctorNumber",)
    list_filter = ("service",)

    def get_full_name(self, obj):
        return (
            obj.user.first_name + " " + obj.user.last_name
        )  # Access the first name of the user associated with the doctor

    get_full_name.short_description = "Full Name"  # Display name for the field

    def get_email(self, obj):
        return obj.user.email  # Access the email of the user associated with the doctor

    get_email.short_description = "Email"  # Display name for the field

    def get_service(self, obj):
        return ", ".join([service.name for service in obj.service.all()])

    get_service.short_description = "Service"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "studentNumber", "get_full_name", "get_email", "user")
    list_editable = ("studentNumber",)
    list_display_links = ("id",)
    search_fields = ("studentNumber",)

    def get_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    get_full_name.short_description = "Full Name"

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"


@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    list_display = ("id", "receptionistNumber", "get_full_name", "get_email", "user")
    list_editable = ("receptionistNumber",)
    list_display_links = ("id",)
    search_fields = ("receptionistNumber",)

    def get_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    get_full_name.short_description = "Full Name"

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"
