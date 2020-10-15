from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from .models import Movie, Rating, MovieGenre, MovieActor
from django.contrib.auth.mixins import LoginRequiredMixin

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
#                 {% if user.is_authenticated %} in template
@login_required
def profile(request):
    return render(request, 'recommender/profile.html')

class RatingListView(LoginRequiredMixin, ListView):
    model = Rating
    template_name = 'recommender/profile.html'
    context_object_name = 'ratings'
    paginate_by = 5

    # filter query so that it only returns current user's ratings
    def get_queryset(self):
        return Rating.objects.filter(who_rated_id=self.request.user)

def new_user(request):
    return render(request, 'recommender/new_user.html')

def recommend(request):
    return render(request, 'recommender/recommend.html')

def users_list(request):
    return render(request, 'recommender/users_list.html')

def add_user(request):
    return render(request, 'recommender/add_user.html')

class MoviesListView(ListView):
    model = Movie
    template_name = 'recommender/movies_list.html'
    context_object_name = 'movies'
    paginate_by = 10


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super(MovieDetailView, self).get_context_data(**kwargs)
        print(Movie.objects.get(pk=self.kwargs.get('pk')))
        context['genres'] = MovieGenre.objects.filter(movie_id=Movie.objects.get(pk=self.kwargs.get('pk')).pk)
        context['actors'] = MovieActor.objects.filter(movie_id=Movie.objects.get(pk=self.kwargs.get('pk')).pk)
        return context
