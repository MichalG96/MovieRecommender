from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Rating

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserRatingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRatingForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget.attrs['min'] = 1
        self.fields['value'].widget.attrs['max'] = 10

    class Meta:
        model = Rating
        fields = ['value']
