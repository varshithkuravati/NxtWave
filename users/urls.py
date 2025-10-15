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

from django.urls import path, include
from django.conf import settings


from . import views

from django.contrib.auth.views import (
    
      PasswordResetView,
      PasswordResetDoneView,
      PasswordResetConfirmView,
      PasswordResetCompleteView,
      PasswordChangeView,
      PasswordChangeDoneView

)
from django.urls import reverse_lazy

app_name = 'users'


urlpatterns = [


    path('signup/',views.signup_view,name='signup'),
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('passwordReset/',PasswordResetView.as_view(
       template_name = 'users/passwordReset.html',
       email_template_name = 'users/passwordResetEmail.html',
       subject_template_name = 'users/passwordResetSubject.txt',
       success_url = reverse_lazy('users:passwordResetDone'),
       from_email = 'varshithkuravti@gmail.com'
   ),name='passwordReset'),

   path('passwordReset/done/',PasswordResetDoneView.as_view(
       template_name = 'users/passwordResetDone.html'),name='passwordResetDone'),

   
   path('reset/<uidb64>/<token>/',PasswordResetConfirmView.as_view(
       template_name = 'users/passwordResetConfirm.html',
       success_url = reverse_lazy('users:passwordResetComplete')
   ),name='passwordResetConfirm'),
   
   
   path('reset/done/',PasswordResetCompleteView.as_view(
       template_name = 'users/passwordResetComplete.html'
   ),name='passwordResetComplete'),

   path('passwordChange/',PasswordChangeView.as_view(
       template_name = 'users/passwordChange.html',
       success_url = reverse_lazy('users:passwordChangeDone')
   ),name='passwordChange'),

   path('passwordChange/done/',PasswordChangeDoneView.as_view(
       template_name = 'users/passwordChangeDone.html'
   ),name = 'passwordChangeDone')





    
]