from django.db import models
from django.db.models import UniqueConstraint
from account.models import Doctor, Student
from doctor.models import Service

# Create your models here.
class Appointment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date_appointment = models.DateField(null=False, blank=False) 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL)
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
    TIME_SCHEDULES = {
        "9h - 9h20": "9h - 9h20",
        "9h30 - 9h50": "9h30 - 9h50",
        "10h - 10h20": "10h - 10h20",
        "10h30 - 10h50": "10h30 - 10h50",
        "11h - 11h20": "11h - 11h20",
        "11h30 - 11h50": "11h30 - 11h50",
        "12h - 12h20": "12h - 12h20",
        "14h - 14h20": "14h - 14h20",
        "14h30 - 14h50": "14h30 - 14h50",
        "15h - 15h20": "15h - 15h20",
        "15h30 - 15h50": "15h30 - 15h50",
        "16h - 16h20": "16h - 16h20",
    }
    time_schedule = models.CharField(max_length=16, choices=TIME_SCHEDULES)

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} at {self.date_appointment.strftime('%Y-%m-%d')}"
    
    #Create the contraint: a user should have only one appointment per day
    class Meta:
        constraints = [
            UniqueConstraint(fields=['date_appointment', 'student'], name='unique_appointment_per_student_per_day')
        ]
    
class Enquiry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    question = models.TextField(max_length=1000)
    answer = models.TextField(max_length=1000, blank=True, null=True)
    is_answering = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry from {self.student.user.username} to {self.doctor.user.username}"