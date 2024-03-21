from django.db import models
from account.models import Doctor, Student
from doctor.models import Service

# Create your models here.
class Appointment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date_appointment = models.DateTimeField(null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL)
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
    TIME_SCHEDULES = {
        "9h-9h20": "9h-9h20",
        "9h30-9h50": "9h30-9h50",
        "10h-10h20": "10h-10h20",
        "10h30-10h50": "10h30-10h50",
        "11h-11h20": "11h-11h20",
        "11h30-11h50": "11h30-11h50",
        "12h-12h20": "12h-12h20",
        "14h-14h20": "14h-14h20",
        "14h30-9h50": "14h30-14h50",
        "15h-15h20": "15h-15h20",
        "15h30-15h50": "15h30-15h50",
        "16h-16h20": "16h-16h20",
    }
    time_schedule = models.CharField(max_length=12, choices=TIME_SCHEDULES)

    def __str__(self):
        return self.student.studentNumber+"  "+self.date_appointment
    
class Enquiry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    question = models.TextField(max_length=1000)
    answer = models.TextField(max_length=1000, blank=True, null=True)
    is_answering = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry from {self.student.user.username} to {self.doctor.user.username}"