from django import forms
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm, UserCreationForm

from .models import CustomUser, Doctor, Receptionist, Service, Student


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "dob",
            "phone",
            "photo",
            "sex",
            "password1",
            "password2",
        ]
        SEX_CHOICES = (
            ("M", "Male"),
            ("F", "Female"),
        )

        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "required": True, "autocomplete": "off"}
            ),
            "first_name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "dob": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "phone": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "photo": forms.FileInput(attrs={"class": "form-control", "required": True}),
            "sex": forms.Select(
                choices=SEX_CHOICES, attrs={"class": "form-control", "required": True}
            ),
            "password1": forms.PasswordInput(
                attrs={"class": "form-control", "required": True, "autocomplete": "off"}
            ),
            "password2": forms.PasswordInput(
                attrs={"class": "form-control", "required": True, "autocomplete": "off"}
            ),
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ["email", "first_name", "last_name", "dob", "phone", "photo", "sex"]
        SEX_CHOICES = (
            ("M", "Male"),
            ("F", "Female"),
        )

        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "required": True, "autocomplete": "off"}
            ),
            "first_name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "dob": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "phone": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "photo": forms.FileInput(attrs={"class": "form-control", "required": True}),
            "sex": forms.Select(
                choices=SEX_CHOICES, attrs={"class": "form-control", "required": True}
            ),
        }


class CustomUserAdminCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name", "role")
        field_classes = {}  # le parent déclare un champ "username" qu'on n'a pas


class CustomUserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = "__all__"
        field_classes = {}


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["studentNumber"]

        widgets = {
            "studentNumber": forms.TextInput(attrs={"class": "form-control", "required": True}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["doctorNumber", "service"]
        service = Service.objects.all()

        widgets = {
            "doctorNumber": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "service": forms.SelectMultiple(attrs={"class": "form-control", "required": True}),
        }


class ReceptionistForm(forms.ModelForm):
    class Meta:
        model = Receptionist
        fields = ["receptionistNumber"]

        widgets = {
            "receptionistNumber": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
        }
