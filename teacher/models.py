from django.db import models

from users.models import User

# Create your models here.


class Course(models.Model):

    name = models.CharField(max_length=100)
    syllabus = models.TextField(null=True, blank=True)


class Teacher(models.Model):

    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    email = models.EmailField(null=True, blank=True)
    teacher_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    

class Document(models.Model):

    title = models.CharField(max_length=100)
    type = models.CharField(max_length=50, default= "reference" ,choices=[('syllabus', 'Syllabus'),('notes', 'Notes'), ('circulum', 'Circulum'), ('reference', 'Reference Material')])
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL,null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL,null=True, blank=True)
    description = models.JSONField(null=True, blank=True)

