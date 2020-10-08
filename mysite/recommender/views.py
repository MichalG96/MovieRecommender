from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def homepage(request):
    return HttpResponse('Strona domowa')

def register(request):
    return HttpResponse('Rejestracja nowego użytkownika')

def new_user(request):
    return HttpResponse('Filmy do ocenienia dla nowego użytkownika')

def recommend(request):
    return HttpResponse('Rekomendacje')