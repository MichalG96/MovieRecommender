from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register', views.register, name='register'),
    path('new_user', views.new_user, name='new_user'),
    path('recommend', views.recommend, name='recommend'),
]
