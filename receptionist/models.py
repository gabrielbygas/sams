from django.db import models
from account.models import Receptionist

# Create your models here.
class Announcement(models.Model):
    date_announcement = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100, blank=False)
    message = models.TextField(max_length=1000, blank=False)
    posted_by = models.ForeignKey(Receptionist, on_delete=models.CASCADE)
    
