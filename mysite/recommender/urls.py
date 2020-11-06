from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (MoviesListView, RatingListView, MovieDetailDispatcherView,
                    UserListView, RatingDeleteView, EstablishPreferencesView,
                    FilteredMovieListView, FilteredRatingListView)
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='recommender/homepage.html'), name='homepage'),
    path('new_user/', views.new_user, name='new_user'),
    path('recommend/<str:username>/', views.recommend, name='recommend'),
    path('qwe/', TemplateView.as_view(template_name='recommender/stars.html'), name='qwe'),
    path('all_users/', UserListView.as_view(), name='all_users'),
    path('add_user/', views.add_user, name='add_user'),
    path('all_movies/', MoviesListView.as_view(), name='all_movies'),
    # path('all_movies_table/', MoviesListTableView.as_view(), name='all_movies_table'),
    path('all_movies_table/', FilteredMovieListView.as_view(), name='all_movies_table'),
    path('profile/<str:username>/', RatingListView.as_view(), name='profile'),
    path('profile_table/<str:username>/', FilteredRatingListView.as_view(), name='profile_table'),
    path('profile/<str:username>/stats/', views.user_stats, name='user_stats'),
    path('preferences/', EstablishPreferencesView.as_view(), name='preferences'),
    path('movie/<int:pk>/', MovieDetailDispatcherView.as_view(), name='movie_detail'),
    path('movie/<int:pk>/delete_rating/', RatingDeleteView.as_view(), name='delete_rating'),
]
