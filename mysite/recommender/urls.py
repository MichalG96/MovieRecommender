from django.urls import path
from . import views
#from users import views as user_views
from django.contrib.auth import views as auth_views
from .views import MoviesListView, RatingListView, MovieDetailView, MovieDetailDispatcherView, RatingCreateView
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='recommender/homepage.html'), name='homepage'),
    path('new_user/', views.new_user, name='new_user'),
    path('recommend/', views.recommend, name='recommend'),
    path('users_list/', views.users_list, name='users_list'),
    path('add_user/', views.add_user, name='add_user'),
    path('all_movies/', MoviesListView.as_view(), name='all_movies'),
    path('profile/', RatingListView.as_view(), name='profile'),
    # path('movie/<int:pk>/', MovieDetailView.as_view(), name='movie_detail'),
    path('movie/<int:pk>/', MovieDetailDispatcherView.as_view(), name='movie_detail'),    #podziel na unseen - dodaj ocenę i seen - edytuj ocenę
    path('movie/<int:pk>/<int:rat_pk>/', MovieDetailDispatcherView.as_view(), name='movie_detail_update_rating'),    #podziel na unseen - dodaj ocenę i seen - edytuj ocenę
    path('rating/new/', RatingCreateView.as_view(), name='add_rating'),

]
