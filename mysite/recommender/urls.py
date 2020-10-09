from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register', views.register, name='register'),
    path('new_user', views.new_user, name='new_user'),
    path('recommend', views.recommend, name='recommend'),
    path('users_list', views.users_list, name='users_list'),
    path('add_user', views.add_user, name='add_user'),
]
