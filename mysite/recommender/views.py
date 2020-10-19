from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView
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
        return self.request.user.rating_set.all()

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

# TODO: pass Movie and Rating objects betweeen views so that you don't have to keep looking them up in the database
class MovieDetailView(DetailView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        print(self.request)
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
        try:
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

class MovieDetailDispatcherView(View):
    # Do this if you received GET request
    def get(self, request, *args, **kwargs):
        print('movie detail test view get')
        view = MovieDetailView.as_view()
        return view(request, *args, **kwargs)

    # Do this if you received POST request
    def post(self, request, *args, **kwargs):
        print('movie detail test view post')
        current_movie = Movie.objects.get(pk=self.kwargs['pk'])
        try:
            # update view
            rat = Rating.objects.get(who_rated=self.request.user.id, movielens_id_id=current_movie.movielens_id)
            print('lecimy z apdejtem')
            view = RatingUpdateView.as_view()

        except ObjectDoesNotExist:
            # create view
            print('no such rating')
            view = RatingCreateView.as_view()

        return view(request, *args, **kwargs)


class RatingCreateView(CreateView):
    model = Rating
    template_name = 'recommender/movie_detail.html'
    form_class = UserRatingForm

    def form_valid(self, form):
        print('create view')
        print(self.request)
        print(self.kwargs)
        form.instance.who_rated = self.request.user
        self.movie_object = Movie.objects.get(pk=self.kwargs['pk'])
        print(Movie.objects.get(pk=self.kwargs['pk']))
        form.instance.movielens_id = self.movie_object
        return super().form_valid(form)

    def get_success_url(self):
        print(Rating.objects.get(who_rated=self.request.user.id, movielens_id_id=self.movie_object.movielens_id).pk)
        return reverse('movie_detail_update_rating', kwargs={'pk': self.kwargs['pk'], 'rat_pk': Rating.objects.get(who_rated=self.request.user.id,
                                                                                                                   movielens_id_id=self.movie_object.movielens_id).pk})

class RatingUpdateView(UpdateView):

    # Error - szuka ratingu o pk podanym w URL (a to pk jest dla filmu)
    model = Rating
    template_name = 'recommender/movie_detail.html'
    form_class = UserRatingForm
    pk_url_kwarg = 'rat_pk'
    print('change')
    # initial = {'value': 5}
    def form_valid(self, form):
        print('update view')
        print(self.request)
        print(self.kwargs)
        print(self.get_object())
        form.instance.who_rated = self.request.user
        movie_object = Movie.objects.get(pk=self.kwargs['pk'])
        form.instance.movielens_id = movie_object
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self))
        return reverse('movie_detail_update_rating', kwargs={'pk': self.kwargs['pk'], 'rat_pk': self.kwargs['rat_pk']})
    #
    # def get_initial(self):
    #     return {
    #         'value': 5,
    #     }
