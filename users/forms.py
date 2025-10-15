from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

class createuser(UserCreationForm):
    class Meta:
        model = User
        fields = ['email','username', 'role']

class loginform(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)