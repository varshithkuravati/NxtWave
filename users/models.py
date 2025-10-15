from django.db import models

from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    email = models.EmailField('email address',unique=True)
    role = models.CharField(max_length=50, choices=[('student', 'Student'), ('teacher', 'Teacher')], default='student')
    # username = models.CharField(max_length=100,default=None)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username