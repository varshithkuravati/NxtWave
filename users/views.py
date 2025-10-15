from django.shortcuts import render, redirect

from . import forms
from .forms import createuser,loginform
from django.contrib.auth import authenticate,login,logout
# Create your views here.


from .models import User
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

import requests
from django.conf import settings
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from datetime import datetime,timedelta
from django.utils import timezone


def signup_view(req):
    if req.user.is_authenticated:
        return redirect('core:home')
        # return redirect('users:form')
    if req.method == "POST":
        form = createuser(req.POST)
        if form.is_valid():
            user1 = form.save()
            login(req,user1)
            messages.success(req,"Account created successfully")
            return redirect('core:home')
            # return redirect('users:form')
        # return HttpResponse("form is not valid")
        return render(req,'users/signup.html',{'form':form})
    
    form = createuser()
    return render(req,'users/signup.html',{'form':form})



def login_view(req):
    if req.user.is_authenticated:
        return redirect('shop:index')
        # return redirect('users:form')
    if req.method == "POST":
        form = loginform(req.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(email=email,password=password)
            if user:

                login(req,user)
               
                messages.success(req,"login successful")
                return redirect('shop:index')  
                # return redirect('users:form') 
            else:
                # messages.error(req,"email or passowrd is incorrect")
                form.add_error(None,'Invalid email or password')

        return render(req,'users/login.html',{'form':form})
    else:
        form = loginform()
        return render(req,'users/login.html',{'form':form})

def logout_view(req):
    logout(req)
    return redirect('shop:index')
