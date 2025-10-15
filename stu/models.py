from django.db import models

from users.models import User

from teacher.models import Course

# Create your models here.


class Student(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    enrolled_courses = models.ManyToManyField(Course, blank=True)
    interest = models.CharField(max_length=200, null=True, blank=True)
    quiz_scores = models.JSONField(null=True, blank=True)

    student_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    


    def __str__(self):
        return self.name