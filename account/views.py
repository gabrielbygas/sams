from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, StudentForm, DoctorForm, ReceptionistForm
from django.contrib.auth import authenticate, login as auth_login, logout  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages                                       
from .models import CustomUser, Student, Doctor, Receptionist
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
def login(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            auth_login(request, login_form.get_user())
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
    else:
        login_form = AuthenticationForm()
    return render(request, 'account/login.html', {'login_form': login_form})

def logout(request):
    return render(request, "account/logout.html")

def user_creation_error_page(request):
    return render(request, "account/user_creation_error_page.html")

#if you are superuser
def is_superuser(user):
    return user.is_superuser

#if you are superuser or receptionist
def is_superuser_or_receptionist(user):
    return user.is_superuser or user.is_receptionist()

#create user
def create_user(user_form):
    user = user_form.save()
    return user

#create custom user (student, doctor, receptionist)
def create_custom_user(user, custom_user_form):
    custom_user = custom_user_form.save(commit=False)
    custom_user.user = user
    custom_user.save()
    return custom_user

#authenticate
def authenticate_and_login(request, user_form):
    email = user_form.cleaned_data['email']
    password = user_form.cleaned_data['password1']
    user = authenticate(username=email, password=password)
    login(request, user)

def create_user_view(request, user_form_class, custom_user_form_class, template_name):
    if request.method == 'POST':
        user_form = user_form_class(request.POST)
        custom_user_form = custom_user_form_class(request.POST)
        if user_form.is_valid() and custom_user_form.is_valid():
            try:
                user = create_user(user_form)
                create_custom_user(user, custom_user_form)
                authenticate_and_login(request, user_form)
                messages.success(request, "You Have Successfully Registered! Welcome!")
                return redirect('home')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        user_form = user_form_class()
        custom_user_form = custom_user_form_class()
    return render(request, template_name, {'user_form': user_form, 'custom_user_form': custom_user_form})

def create_student(request):
    return create_user_view(request, CustomUserCreationForm, StudentForm, 'account/create_student.html')

@login_required
@user_passes_test(is_superuser_or_receptionist, login_url='user_creation_error_page')
def create_doctor(request):
    return create_user_view(request, CustomUserCreationForm, DoctorForm, 'account/create_doctor.html')

@login_required
@user_passes_test(is_superuser, login_url='user_creation_error_page')
def create_receptionist(request):
    return create_user_view(request, CustomUserCreationForm, ReceptionistForm, 'account/create_receptionist.html')

@login_required
def user_creation_error_page(request):
    context = {}
    if not request.user.is_superuser and not request.user.is_receptionist():
        context['error_message'] = "Only an Admin or receptionist can access this page."
    elif not request.user.is_receptionist():
        context['error_message'] = "Only a receptionist can access this page."
    return render(request, "account/user_creation_error_page.html", context)
