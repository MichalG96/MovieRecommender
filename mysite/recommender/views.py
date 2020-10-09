from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
import pandas as pd
# Create your views here.

def homepage(request):
    return render(request, 'recommender/homepage.html')

def register(request):
    return render(request, 'recommender/register.html')

def new_user(request):
    return render(request, 'recommender/new_user.html')

def recommend(request):
    return render(request, 'recommender/recommend.html')

def users_list(request):
    return render(request, 'recommender/users_list.html')




# one-time view for addding mockup users from csv file
users = pd.read_csv('users.csv')
def add_user(request):
    for i, row in users.iterrows():
        user = User.objects.create_user(
            username=row['username'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            password=row['password'],
            email=row['email'],
            date_joined=row['date_joined'])
    return HttpResponse('elo')