from django.shortcuts import render

# Create your views here.

def homepage(request):
    return render(request, 'recommender/homepage.html')

def register(request):
    return render(request, 'recommender/register.html')

def new_user(request):
    return render(request, 'recommender/new_user.html')

def recommend(request):
    return render(request, 'recommender/recommend.html')
