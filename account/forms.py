from django import forms
from .models import CustomUser, Student, Receptionist, Doctor
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'dob', 'phone', 'photo', 'sex']
        

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'sex': forms.RadioSelect(attrs={'class': 'form-control'}),
        }
    
   
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'dob', 'phone', 'photo', 'sex']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'sex': forms.RadioSelect(attrs={'class': 'form-control'}),
        }
    

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['studentNumber']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['doctorNumber', 'service']

class ReceptionistForm(forms.ModelForm):
    class Meta:
        model = Receptionist
        fields = ['receptionistNumber']
