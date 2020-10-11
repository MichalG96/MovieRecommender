from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required

import pandas as pd
# Create your views here.

def homepage(request):
    return render(request, 'recommender/homepage.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')    # TODO: change language
            return redirect('homepage')
    else:
        form = UserRegisterForm()
    return render(request, 'recommender/register.html', {'form': form})
    # return render(request, 'recommender/register.html')


# TODO: part of a profile (photo, username) has to be visible by any other LOGGED IN user
@login_required
def profile(request):
    return render(request, 'recommender/profile.html')



def new_user(request):
    return render(request, 'recommender/new_user.html')

def recommend(request):
    return render(request, 'recommender/recommend.html')

def users_list(request):
    return render(request, 'recommender/users_list.html')




# TODO: redo this view, find out why only 416 out of 422 users where added
# one-time view for addding mockup users from csv file
# users = pd.read_csv('users.csv')
def add_user(request):
#     for i, row in users.iterrows():
#         user = User.objects.create_user(
#             username=row['username'],
#             first_name=row['first_name'],
#             last_name=row['last_name'],
#             password=row['password'],
#             email=row['email'],
#             date_joined=row['date_joined'])
    return HttpResponse('elo')