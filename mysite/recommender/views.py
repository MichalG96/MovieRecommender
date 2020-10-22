from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from .models import Movie, Rating, Actor, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserRatingForm, MovieSortForm, MovieRatingSortForm, MovieGroupForm, MovieRatingGroupForm
from django.utils.datastructures import MultiValueDictKeyError
import requests

base_tmbd_url = 'https://api.themoviedb.org/3/movie/'
api_key = 'bef647566a5b4968a35cd34a79dc3dce'
base_img_url = 'https://image.tmdb.org/t/p/'
# available sizes :"w92", "w154"," w185", "w342", "w500", "w780", "original"
img_size = 'w342/'

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

# TODO: part of a profile (photo, username) has to be visible by any other LOGGED IN user
# ({% if user.is_authenticated %} in template)

class RatingListView(LoginRequiredMixin, ListView):
    model = Movie
    template_name = 'recommender/profile.html'
    context_object_name = 'ratings'
    paginate_by = 7
    ordering = 'id'

    # Filter query so that it only returns current user's ratings
    def get_queryset(self):
        ordering = self.get_ordering()
        if ordering:
            if 'value' in ordering or 'date_rated' in ordering:
                return self.request.user.rating_set.all().order_by(ordering)
            else:
                if ordering.startswith('-'):
                    return self.request.user.rating_set.all().order_by(f'-movielens_id__{self.get_ordering()[1:]}')
                else:
                    return self.request.user.rating_set.all().order_by(f'movielens_id__{self.get_ordering()}')
        else:
            return self.request.user.rating_set.all()

    def get_ordering(self):
        try:
            ordering = self.request.GET['sort_by']
        except MultiValueDictKeyError:
            ordering = super().get_ordering()
        return ordering

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_sorting'] = MovieRatingSortForm(self.request.GET)
        context['sort_by'] = self.get_ordering()
        context['form_grouping'] = MovieRatingGroupForm(self.request.GET)
        return context


class MoviesListView(ListView):
    model = Movie
    context_object_name = 'movies'
    paginate_by = 15
    ordering = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        upper_decades_limits = self.get_grouping()
        if upper_decades_limits:
            print(upper_decades_limits)
            movies_from_decades = queryset.filter(year_released__gte=(upper_decades_limits[0]-9),
                                                 year_released__lte=(upper_decades_limits[0]))
            for limit in upper_decades_limits[1:]:
                movies_from_decades |= queryset.filter(year_released__gte=(limit-9),
                                                 year_released__lte=(limit))
            return movies_from_decades
        else:
            return queryset

    def get_grouping(self):
        if self.request.GET.__contains__('group_by_decades'):
            decades = list(map(int, self.request.GET.getlist('group_by_decades')))
            self.extra_context = {'group_by': decades}

            return decades
        else:
            return None

    def get_ordering(self):
        if self.request.GET.__contains__('sort_by'):
            return self.request.GET['sort_by']
        else:
            return super().get_ordering()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_sorting_grouping'] = MovieSortForm(self.request.GET)
        context['sort_by'] = self.get_ordering()
        # context['form_grouping'] = MovieGroupForm(self.request.GET)

        # context['movies']=(self.object_list.filter(year_released__gt=2010))
        # print(context['movies'].filter(year_released__gt=2010))
        # print()
        print(context)

        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tmdb_id = self.object.tmdb_id
        url = f'{base_tmbd_url}{tmdb_id}?api_key={api_key}'
        url_credits = f'{base_tmbd_url}{tmdb_id}/credits?api_key={api_key}'
        r = requests.get(url).json()
        genres = [genre_dict['name'] for genre_dict in r['genres']]
        overview = r['overview']
        img_url = f'{base_img_url}{img_size}{r["poster_path"]}'
        r_credits = requests.get(url_credits).json()
        cast = [{'name': person['name'], 'character': person['character']} for person in r_credits['cast'][:8]]
        context['actors'] = self.object.actor_set.all()
        context['genres'] = self.object.genre_set.all()
        try:
            context['rating'] = self.object.rating_set.all().get(who_rated=self.request.user.id)
        except ObjectDoesNotExist:
            context['rating'] = None
        context['genres_tmdb'] = genres
        context['overview'] = overview
        context['cast_tmdb'] = cast
        context['img_url'] = img_url
        if context['rating']:
            initial_value = context['rating'].value
            context['rating_exists'] = True
        else:
            initial_value = None
            context['rating_exists'] = False

        context['form'] = UserRatingForm(initial={'value': initial_value})

        return context

class MovieDetailDispatcherView(View):
    # Do this if you received GET request
    def get(self, request, *args, **kwargs):
        view = MovieDetailView.as_view()
        return view(request, *args, **kwargs)

    # Do this if you received POST request
    def post(self, request, *args, **kwargs):
        current_movie = Movie.objects.get(pk=self.kwargs['pk'])
        try:
            # Update view
            Rating.objects.get(who_rated=self.request.user.id, movielens_id_id=current_movie.movielens_id)
            view = RatingUpdateView.as_view()

        except ObjectDoesNotExist:
            # Create view
            view = RatingCreateView.as_view()
        return view(request, *args, **kwargs)

class RatingCreateView(CreateView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    form_class = UserRatingForm

    def form_valid(self, form):
        form.instance.who_rated = self.request.user
        self.movie_object = Movie.objects.get(pk=self.kwargs['pk'])
        form.instance.movielens_id = self.movie_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'pk': self.kwargs['pk']})

class RatingUpdateView(UserPassesTestMixin, UpdateView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    form_class = UserRatingForm

    # Tell the view, that you do not want to modify the Movie object, but rather Rating object related to this movie
    def get_object(self, *args, **kwargs):
        obj = super().get_object()
        # This should not throw MultipleObjectsReturned error, because there is UniqueConstraint
        # asserting that there is only one rating per movie-user pair,
        # nor should it throw ObjectDoesNotExist because this view is executed only when the Rating object exists
        new_obj = obj.rating_set.get(who_rated=self.request.user.id)
        return new_obj

    def form_valid(self, form):
        form.instance.who_rated = self.request.user
        movie_object = self.get_object().movielens_id
        form.instance.movielens_id = movie_object
        return super().form_valid(form)

    def test_func(self):
        rating = self.get_object()
        if self.request.user == rating.who_rated:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'pk': self.kwargs['pk']})

class RatingDeleteView(UserPassesTestMixin, DeleteView):
    model = Movie
    # template_name = 'recommender/movie_detail.html'

    def get_object(self, *args, **kwargs):
        obj = super().get_object()
        new_obj = obj.rating_set.get(who_rated=self.request.user.id)
        return new_obj

    def test_func(self):
        rating = self.get_object()
        if self.request.user == rating.who_rated:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'pk': self.kwargs['pk']})

def new_user(request):
    return render(request, 'recommender/new_user.html')

def recommend(request):
    return render(request, 'recommender/recommend.html')

def users_list(request):
    return render(request, 'recommender/users_list.html')

def add_user(request):
    return render(request, 'recommender/add_user.html')
