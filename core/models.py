from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN','Admin'),
        ('TEACHER','Teacher'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TEACHER')

class SchoolClass(models.Model):
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=5, blank=True, null=True)
    class_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role':'TEACHER'},
        related_name="assigned_classes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.class_name} {self.section if self.section else ''}".strip()