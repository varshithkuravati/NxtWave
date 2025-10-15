"""
URL configuration for student project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views


app_name = 'stu'

urlpatterns = [

    path('dashboard/', views.stu_dashboard, name='stu_dashboard'),
    path('quizGen/', views.quizGen, name='quizGen'),

    path('quizpage/', views.quizpage, name='quizpage'),
    path('quizResults/', views.quiz_results, name='quizResults'),
    path('aiTutorChat/', views.chat_ai, name='aiTutorChat'),
    path('contentClarifier/',views.content_clarifier, name='contentClarifier'),


    

    
]