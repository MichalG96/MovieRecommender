from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import MoviesListView, RatingListView, MovieDetailDispatcherView, RatingDeleteView, EstablishPreferencesView
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='recommender/homepage.html'), name='homepage'),
    path('new_user/', views.new_user, name='new_user'),
    path('recommend/', views.recommend, name='recommend'),
    path('qwe/', TemplateView.as_view(template_name='recommender/stars.html'), name='qwe'),
    path('users_list/', views.users_list, name='users_list'),
    path('add_user/', views.add_user, name='add_user'),
    path('all_movies/', MoviesListView.as_view(), name='all_movies'),
    # TODO: although i'm not using this url, when i comment this out django throws an error
    # Find out why (probably it's used in some other place in code)
    path('profile/', RatingListView.as_view(), name='profile'),
    path('profile/<str:username>/', RatingListView.as_view(), name='profile'),
    path('preferences/', EstablishPreferencesView.as_view(), name='preferences'),
    path('movie/<int:pk>/', MovieDetailDispatcherView.as_view(), name='movie_detail'),
    path('movie/<int:pk>/delete_rating/', RatingDeleteView.as_view(), name='delete_rating'),
]
