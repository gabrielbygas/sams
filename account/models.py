from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from doctor.models import Service


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is REQUIRED!")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Role choices for CustomUser
    class Role(models.TextChoices):
        STUDENT = "student", "Student"  # valeur en base, libellé affiché
        DOCTOR = "doctor", "Doctor"
        RECEPTIONIST = "receptionist", "Receptionist"

    email = models.EmailField(verbose_name="Email", unique=True, max_length=250, blank=False)
    first_name = models.CharField(max_length=100, null=True)  # null=True to save a supeeruser
    last_name = models.CharField(max_length=100, null=True)  # null=True to save a supeeruser
    role = models.CharField(max_length=20, choices=Role.choices, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    photo = models.ImageField(upload_to="user_photos/", null=True, blank=True)
    SEX_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
    )
    sex = models.CharField(
        max_length=1, choices=SEX_CHOICES, null=True
    )  # null=True to save a supeeruser
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    objects = MyUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(is_superuser=True) | ~Q(role=""),
                name="role_required_unless_superuser",
            ),
        ]

    # If CustomUser is doctor, necessary for user permissions (account.views)
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    # If CustomUser is receptionist, necessary for user permissions (account.views)
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    # If CustomUser is receptionist, necessary for user permissions (account.views)
    def is_student(self):
        return self.role == self.Role.STUDENT

    def has_role(self, *roles):
        """True si l'utilisateur a l'un des rôles donnés. Le superuser a tous les rôles."""
        return self.is_superuser or self.role in roles

    def __str__(self):
        full_name = ""
        if self.first_name:
            full_name += self.first_name
        if self.last_name:
            full_name += "." + self.last_name
        if full_name:
            return full_name + "  >  " + self.email
        else:
            return self.email


class RoleProfileMixin:
    """Un profil ne peut être rattaché qu'à un compte du rôle correspondant."""

    required_role = None

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != self.required_role:
            raise ValidationError(
                {"user": f"This account does not have the {self.required_role} role."}
            )


# Student is a custom user
class Student(RoleProfileMixin, models.Model):
    required_role = CustomUser.Role.STUDENT

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    studentNumber = models.CharField(
        verbose_name="Student Number", max_length=10, unique=True, blank=False, null=False
    )

    def __str__(self):
        return self.user.first_name + "." + self.user.last_name + " / " + self.studentNumber


# Doctor is a custom user
class Doctor(RoleProfileMixin, models.Model):
    required_role = CustomUser.Role.DOCTOR

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    doctorNumber = models.CharField(
        verbose_name="Doctor Number", max_length=10, unique=True, blank=False, null=False
    )
    service = models.ManyToManyField(Service)

    def __str__(self):
        return self.user.first_name + "." + self.user.last_name + " / " + self.doctorNumber


# Receptionist is a custom user
class Receptionist(RoleProfileMixin, models.Model):
    required_role = CustomUser.Role.RECEPTIONIST

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    receptionistNumber = models.CharField(
        verbose_name="Receptionist Number", max_length=10, unique=True, blank=False, null=False
    )

    def __str__(self):
        return self.user.first_name + "." + self.user.last_name + " / " + self.receptionistNumber
