from django.urls import path
from . import views
#from users import views as user_views
from django.contrib.auth import views as auth_views
from .views import MoviesListView, RatingListView, MovieDetailView, MovieDetailTestView, RatingCreateView

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('new_user/', views.new_user, name='new_user'),
    path('recommend/', views.recommend, name='recommend'),
    path('users_list/', views.users_list, name='users_list'),
    path('add_user/', views.add_user, name='add_user'),
    path('all_movies/', MoviesListView.as_view(), name='all_movies'),
    path('profile/', RatingListView.as_view(), name='profile'),
    # path('movie/<int:pk>/', MovieDetailView.as_view(), name='movie_detail'),
    path('movie/<int:pk>/', MovieDetailTestView.as_view(), name='movie_detail'),
    path('rating/new/', RatingCreateView.as_view(), name='add_rating'),


    # path('login/', auth_views.LoginView.as_view(template_name='recommender/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='recommender/logout.html'), name='logout'),
    # path('register/', views.register, name='register'),

]
