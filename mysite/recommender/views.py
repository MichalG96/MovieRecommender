from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views import View
from .models import Movie, Rating, MovieGenre, MovieActor
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserRatingForm
from django.utils import timezone

import requests

base_tmbd_url = 'https://api.themoviedb.org/3/movie/'
api_key = 'bef647566a5b4968a35cd34a79dc3dce'
base_img_url = 'https://image.tmdb.org/t/p/'
# available sizes :"w92", "w154"," w185", "w342", "w500", "w780", "original"
img_size = 'w342/'

def homepage(request):
    return render(request, 'recommender/homepage.html')

def register(request):
    # TODO: try the same logic with adding ratings
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
    paginate_by = 15

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super(MovieDetailView, self).get_context_data(**kwargs)
        # current_movie = Movie.objects.get(pk=self.kwargs.get("pk"))
        current_movie = self.get_object()     # self.object returns the same result
        tmdb_id = current_movie.tmdb_id
        url = f'{base_tmbd_url}{tmdb_id}?api_key={api_key}'
        url_credits = f'{base_tmbd_url}{tmdb_id}/credits?api_key={api_key}'

        r = requests.get(url).json()
        genres = [genre_dict['name'] for genre_dict in r['genres']]
        overview = r['overview']
        img_url = f'{base_img_url}{img_size}{r["poster_path"]}'

        r_credits = requests.get(url_credits).json()
        cast = [{'name': person['name'], 'character': person['character']} for person in r_credits['cast'][:8]]

        context['genres'] = MovieGenre.objects.filter(movie_id=Movie.objects.get(pk=self.kwargs.get('pk')).pk)
        context['actors'] = MovieActor.objects.filter(movie_id=Movie.objects.get(pk=self.kwargs.get('pk')).pk)
        print(self.request.user.id)
        try:
            print(current_movie.movielens_id)
            # context['rating'] = Rating.objects.get(who_rated=self.request.user.id, movie=current_movie.id)
            context['rating'] = Rating.objects.get(who_rated=self.request.user.id, movielens_id_id=current_movie.movielens_id)
            print(context['rating'])
        except ObjectDoesNotExist:
            context['rating'] = None
        context['genres_tmdb'] = genres
        context['overview'] = overview
        context['cast_tmdb'] = cast
        context['img_url'] = img_url
        context['form'] = UserRatingForm()

        # if self.request.method == 'POST':
        #     print('form gitaras')
        #
        #     form = RatingForm(self.request.POST)
        #     if form.is_valid():
        #         form.save()
        # else:
        #     form = RatingForm()

        return context

class UserRating(LoginRequiredMixin, SingleObjectMixin, FormView):
    template_name = 'recommender/movie_detail.html'
    form_class = UserRatingForm
    model = Movie

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


    def form_valid(self, form):     # if form is valid then do this
        form.instance.who_rated = self.request.user
        # form.instance.movielens_id = Movie.objects.get(pk=self.kwargs['pk'])
        form.instance.movielens_id = self.object
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.is_valid())
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'pk': self.object.pk})

class MovieDetailTestView(View):
    def get(self, request, *args, **kwargs):
        print('movie detail test view get')
        view = MovieDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # rate_movie(request)       #ostatnio probowalem tego
        # print('movie detail test view  post')
        view = UserRating.as_view()
        # view = MovieDetailView.as_view()

        return view(request, *args, **kwargs)


class RatingCreateView(CreateView):
    model = Rating
    fields = ['value', 'movielens_id']
    template_name = 'recommender/add_rating.html'
    success_url = '/'
    def form_valid(self, form):
        print(self.request)
        form.instance.who_rated = self.request.user
        # form.instance.movielens_id = 5
        #form.instance.movielens_id = jakoś z url
        return super().form_valid(form)