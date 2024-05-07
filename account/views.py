from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, StudentForm, DoctorForm, ReceptionistForm
from django.contrib.auth import authenticate, login, logout  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
def auth_login(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        next_url = ''
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            if request.GET.get('next'): #if @login_required
                next_url = request.GET.get('next')
            elif user.is_doctor(): #if user is doctor
                next_url = 'doctors:home'
            elif user.is_receptionist(): #if user is receptionist
                next_url = 'receptionists:home'
            elif user.is_student(): #if user is student
                next_url = 'students:home' 
            else:
                next_url = 'home'
            return redirect(next_url)
    else:
        login_form = AuthenticationForm()
    return render(request, 'account/login.html', {'login_form': login_form})

def auth_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You Have Been Logged Out...")
    return redirect('home')

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

def create_user_view(request, user_form_class, custom_user_form_class, template_name, redirect_to):
    if request.method == 'POST': #if POST Request
        user_form = user_form_class(request.POST, request.FILES)
        custom_user_form = custom_user_form_class(request.POST)
        try:
            if not user_form.is_valid(): #if user_form is not valid
                for field, errors in user_form.errors.items():
                    for error in errors: # so, print all fields errors
                        messages.error(request, f"User Form Error, field ' {field} ' : {error} \n")
            if not custom_user_form.is_valid(): #if custom_user_form is not valid
                for field, errors in custom_user_form.errors.items():
                    for error in errors: # so, print all fields errors
                        messages.error(request, f"Custom User Form Error, field ' {field} ' : {error} \n")
            if user_form.is_valid() and custom_user_form.is_valid():
                try:
                    user = create_user(user_form)
                    custom_user = create_custom_user(user, custom_user_form)
                    
                    #if the custom_user is a doctor, so he has a service field
                    if(custom_user_form.cleaned_data.get('service')):
                         # Get the services from the form
                        services = custom_user_form.cleaned_data.get('service')
                        # Add the services to the doctor
                        for service in services:
                            custom_user.service.add(service)
                        custom_user.save()

                    authenticate_and_login(request, user_form)
                    messages.success(request, "You Have Successfully Registered! Welcome!")
                    return redirect(redirect_to)
                except Exception as e: # if all form are valid, so an error occured during user creation (create_user and/or create_custom_user function) or aunthentication (auntenticate_and_login function)
                    messages.error(request, f"Your Form is Valid But an Unexpected error occurred during user creation or authentication: {e}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    else: # GET Request
        user_form = user_form_class()
        custom_user_form = custom_user_form_class()
    return render(request, template_name, {'user_form': user_form, 'custom_user_form': custom_user_form})


def create_student(request):
    return create_user_view(request, CustomUserCreationForm, StudentForm, 'account/create_student.html', 'students:home')

@login_required
@user_passes_test(is_superuser_or_receptionist, login_url='accounts:user_creation_error_page')
def create_doctor(request):
    return create_user_view(request, CustomUserCreationForm, DoctorForm, 'account/create_doctor.html', 'doctors:home')

@login_required
@user_passes_test(is_superuser, login_url='accounts:user_creation_error_page')
def create_receptionist(request):
    return create_user_view(request, CustomUserCreationForm, ReceptionistForm, 'account/create_receptionist.html', 'receptionists:home')

@login_required
def user_creation_error_page(request):
    context = {}
    if not request.user.is_superuser and not request.user.is_receptionist():
        context['error_message'] = "Only an Admin or Receptionist can access this page."
    elif not request.user.is_receptionist():
        context['error_message'] = "Only a Receptionist can access this page."
    return render(request, "account/user_creation_error_page.html", context)
