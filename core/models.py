from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
from django.utils.crypto import get_random_string

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
    
class Student(models.Model):
    student_uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    full_name = models.CharField(max_length=120)
    roll_no = models.PositiveIntegerField()
    
    student_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="students"
    )
    
    guardian_mobile = models.CharField(max_length=15, blank=True, null=True)
    
    verification_key = models.CharField(max_length=50, editable=False)
    
    qr_code_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        if not self.verification_key:
            self.verification_key = get_random_string(20)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.student_class}"