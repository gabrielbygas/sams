from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, name=None, surname=None, dob=None, phone=None, 
                    photo=None, sex=None, created_at=None):
        if not email:
            raise ValueError(" Email field is REQUIRED !")
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            dob=dob,
            phone=phone,
            photo=photo,
            sex=sex,
            created_at=created_at
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, name=None, surname=None, dob=None, phone=None, 
                    photo=None, sex=None, created_at=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            name=name,
            surname=surname,
            dob=dob,
            phone=phone,
            photo=photo,
            sex=sex,
            created_at=created_at
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name="email address", unique=True, max_length=256, blank=False)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    objects = MyUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

# Student is a custom user
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    studentNumber = models.CharField(max_length=10)


# Doctor is a custom user
class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    doctorNumber = models.CharField(max_length=10)


# Receptionist is a custom user
class Receptionist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    receptionistNumber = models.CharField(max_length=10)
