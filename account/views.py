from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm, DoctorForm, ReceptionistForm, StudentForm
from .models import CustomUser

ROLE_HOME = {
    CustomUser.Role.STUDENT: "students:home",
    CustomUser.Role.DOCTOR: "doctors:home",
    CustomUser.Role.RECEPTIONIST: "receptionists:home",
}


# Create your views here.
def auth_login(request):
    if request.method == "POST":
        login_form = AuthenticationForm(request, data=request.POST)
        next_url = ""
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            next_url = request.GET.get("next") or ROLE_HOME.get(user.role, "home")
            return redirect(next_url)
    else:
        login_form = AuthenticationForm()
    return render(request, "account/login.html", {"login_form": login_form})


def auth_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You Have Been Logged Out...")
    return redirect("home")


# if you are superuser
def is_superuser(user):
    return user.is_superuser


# if you are superuser or receptionist
def is_superuser_or_receptionist(user):
    return user.has_role(CustomUser.Role.RECEPTIONIST)


# create user
def create_user(user_form, role):
    user = user_form.save(commit=False)
    user.role = role
    user.save()
    return user


# create custom user (student, doctor, receptionist)
def create_custom_user(user, custom_user_form):
    custom_user = custom_user_form.save(commit=False)
    custom_user.user = user
    custom_user.save()
    return custom_user


# authenticate
def authenticate_and_login(request, user_form):
    email = user_form.cleaned_data["email"]
    password = user_form.cleaned_data["password1"]
    user = authenticate(username=email, password=password)
    login(request, user)


def create_user_view(
    request, user_form_class, custom_user_form_class, template_name, redirect_to, role
):
    if request.method == "POST":  # if POST Request
        user_form = user_form_class(request.POST, request.FILES)
        custom_user_form = custom_user_form_class(request.POST)
        try:
            if not user_form.is_valid():  # if user_form is not valid
                for field, errors in user_form.errors.items():
                    for error in errors:  # so, print all fields errors
                        messages.error(request, f"User Form Error, field ' {field} ' : {error} \n")
            if not custom_user_form.is_valid():  # if custom_user_form is not valid
                for field, errors in custom_user_form.errors.items():
                    for error in errors:  # so, print all fields errors
                        messages.error(
                            request, f"Custom User Form Error, field ' {field} ' : {error} \n"
                        )
            if user_form.is_valid() and custom_user_form.is_valid():
                try:
                    with transaction.atomic():
                        user = create_user(user_form, role)
                        custom_user = create_custom_user(user, custom_user_form)

                        # if the custom_user is a doctor, so he has a service field
                        if custom_user_form.cleaned_data.get("service"):
                            # Get the services from the form
                            services = custom_user_form.cleaned_data.get("service")
                            custom_user.service.set(services)

                    authenticate_and_login(request, user_form)
                    messages.success(request, "You Have Successfully Registered! Welcome!")
                    return redirect(redirect_to)
                except Exception as e:  # if all form are valid, so an error occured during user creation (create_user and/or create_custom_user function) or aunthentication (auntenticate_and_login function)
                    messages.error(
                        request,
                        f"Your Form is Valid But an Unexpected error occurred during user creation or authentication: {e}",
                    )
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    else:  # GET Request
        user_form = user_form_class()
        custom_user_form = custom_user_form_class()
    return render(
        request, template_name, {"user_form": user_form, "custom_user_form": custom_user_form}
    )


def create_student(request):
    return create_user_view(
        request,
        user_form_class=CustomUserCreationForm,
        custom_user_form_class=StudentForm,
        template_name="account/create_student.html",
        redirect_to="students:home",
        role=CustomUser.Role.STUDENT,
    )


@login_required
@user_passes_test(is_superuser_or_receptionist, login_url="accounts:user_creation_error_page")
def create_doctor(request):
    return create_user_view(
        request,
        user_form_class=CustomUserCreationForm,
        custom_user_form_class=DoctorForm,
        template_name="account/create_doctor.html",
        redirect_to="doctors:home",
        role=CustomUser.Role.DOCTOR,
    )


@login_required
@user_passes_test(is_superuser, login_url="accounts:user_creation_error_page")
def create_receptionist(request):
    return create_user_view(
        request,
        user_form_class=CustomUserCreationForm,
        custom_user_form_class=ReceptionistForm,
        template_name="account/create_receptionist.html",
        redirect_to="receptionists:home",
        role=CustomUser.Role.RECEPTIONIST,
    )


@login_required
def user_creation_error_page(request):
    if request.user.has_role(CustomUser.Role.RECEPTIONIST):
        error_message = "Only an Admin can create a receptionist."
    else:
        error_message = "Only an Admin or a Receptionist can create this account."
    return render(
        request, "account/user_creation_error_page.html", {"error_message": error_message}
    )
