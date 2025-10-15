from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from stu.models import Student
from teacher.models import Teacher

@receiver(post_save,sender=User)

def create_profile(sender,instance,created,**kwargs):
    if created:
        if instance.role == 'student':

            Student.objects.create(student_user=instance)
        elif instance.role == 'teacher':

            Teacher.objects.create(teacher_user=instance)
