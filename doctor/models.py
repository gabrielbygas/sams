from django.db import models

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']