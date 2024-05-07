from django.db import models
from doctor.models import Service
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, dob=None, phone=None, 
                    photo=None, sex=None, created_at=None):
        if not email:
            raise ValueError(" Email field is REQUIRED !")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            phone=phone,
            photo=photo,
            sex=sex,
            created_at=created_at
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, first_name=None, last_name=None, dob=None, phone=None, 
                    photo=None, sex=None, created_at=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name,
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
    email = models.EmailField(verbose_name="Email", unique=True, max_length=250, blank=False)
    first_name = models.CharField(max_length=100, null=True) #null=True to save a supeeruser
    last_name = models.CharField(max_length=100, null=True) #null=True to save a supeeruser
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True) #null=True to save a supeeruser
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    objects = MyUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    #If CustomUser is doctor, necessary for user permissions (account.views)
    def is_doctor(self):
        return hasattr(self, 'doctor')

    #If CustomUser is receptionist, necessary for user permissions (account.views)
    def is_receptionist(self):
        return hasattr(self, 'receptionist')
    
    #If CustomUser is receptionist, necessary for user permissions (account.views)
    def is_student(self):
        return hasattr(self, 'student')

    def __str__(self):
        full_name = ''
        if self.first_name:
            full_name += self.first_name
        if self.last_name:
            full_name += '.' + self.last_name
        if full_name:
            return full_name + '  >  ' + self.email
        else:
            return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

# Student is a custom user
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    studentNumber = models.CharField(verbose_name="Student Number", max_length=10, unique=True, blank=False, null=False)

    def __str__(self):
        return self.user.first_name + '.' + self.user.last_name + ' / ' + self.studentNumber

# Doctor is a custom user
class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    doctorNumber = models.CharField(verbose_name="Doctor Number", max_length=10, unique=True, blank=False, null=False)
    service = models.ManyToManyField(Service)

    def __str__(self):
        return self.user.first_name + '.' + self.user.last_name + ' / ' + self.doctorNumber


# Receptionist is a custom user
class Receptionist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    receptionistNumber = models.CharField(verbose_name="Receptionist Number", max_length=10, unique=True, blank=False, null=False)

    def __str__(self):
        return self.user.first_name + '.' + self.user.last_name + ' / ' + self.receptionistNumber