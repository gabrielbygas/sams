from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, StudentForm, DoctorForm, ReceptionistForm
from .models import CustomUser, Student, Doctor, Receptionist
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
def signup(request):
    return render(request, "account/signup.html")

def logout(request):
    return render(request, "account/logout.html")

def user_creation_error_page(request):
    return render(request, "account/user_creation_error_page.html")

def is_superuser(user):
    return user.is_superuser

def is_superuser_or_receptionist(user):
    return user.is_superuser or user.is_receptionist()

@login_required
@user_passes_test(is_superuser_or_receptionist, login_url='user_creation_error_page')
def create_student(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        student_form = StudentForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            return redirect('home')
    else:
        user_form = CustomUserCreationForm()
        student_form = StudentForm()
    return render(request, 'account/create_student.html', {'user_form': user_form, 'student_form': student_form})

@login_required
@user_passes_test(is_superuser_or_receptionist, login_url='user_creation_error_page')
def create_doctor(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        doctor_form = DoctorForm(request.POST)
        if user_form.is_valid() and doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            return redirect('home')
    else:
        user_form = CustomUserCreationForm()
        doctor_form = DoctorForm()
    return render(request, 'account/create_doctor.html', {'user_form': user_form, 'doctor_form': doctor_form})

@login_required
@user_passes_test(is_superuser, login_url='user_creation_error_page')
def create_receptionist(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        receptionist_form = ReceptionistForm(request.POST)
        if user_form.is_valid() and receptionist_form.is_valid():
            user = user_form.save()
            receptionist = receptionist_form.save(commit=False)
            receptionist.user = user
            receptionist.save()
            return redirect('home')
    else:
        user_form = CustomUserCreationForm()
        receptionist_form = ReceptionistForm()
    return render(request, 'account/create_receptionist.html', {'user_form': user_form, 'receptionist_form': receptionist_form})
