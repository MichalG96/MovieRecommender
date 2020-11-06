from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from .models import Movie, Rating, Actor, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserRegisterForm, UserRatingForm, MovieSortGroupForm, MovieRatingSortGroupForm
from django.db.models import Avg, Count, Max, Min, Prefetch

# Third - party Django modules
import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django_tables2.views import SingleTableMixin

import django_filters
from django_filters.views import FilterView


from plotly.offline import plot
import plotly.graph_objects as go
import requests
from datetime import timedelta
import pandas as pd
import numpy as np
from collections import Counter

base_tmbd_url = 'https://api.themoviedb.org/3/movie/'
api_key = 'bef647566a5b4968a35cd34a79dc3dce'
base_img_url = 'https://image.tmdb.org/t/p/'
# available sizes :"w92", "w154"," w185", "w342", "w500", "w780", "original"
img_size = 'w185/'



class MovieFilter(django_filters.FilterSet):
    class Meta:
        model = Movie
        fields = ['imdb_id']

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
    paginate_by = 10

    def group_by_decade(self, queryset, decades_grouping):
        upper_decades_limits = list(map(int, decades_grouping))
        movies_from_decades = queryset.filter(
            movie__year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
        for limit in upper_decades_limits[1:]:
            movies_from_decades |= queryset.filter(movie__year_released__range=[(limit - 9), (limit)])
        # Consists only of movies from decades defined by the user
        return movies_from_decades

    def group_by_rating(self, queryset, ratings_grouping):
        possible_ratings = list(map(int, ratings_grouping))
        movies_with_ratings = queryset.filter(value=possible_ratings[0])
        for rating in possible_ratings[1:]:
            movies_with_ratings |= queryset.filter(value=rating)
        # Consists only of movies from decades and with ratings defined by the user
        return movies_with_ratings

    def get_queryset(self):
        # self.profile_owner = User.objects.get(username=self.kwargs['username'])
        self.profile_owner = User.objects.prefetch_related(
            Prefetch(
                'rating_set',
            )).get(username=self.kwargs['username'])

        queryset = self.profile_owner.rating_set.all()
        self.form = MovieRatingSortGroupForm(self.request.GET)

        if self.form.is_valid():
            decades_grouping = self.form.cleaned_data['group_by_decades']
            ratings_grouping = self.form.cleaned_data['group_by_ratings']
            if decades_grouping:
                queryset = self.group_by_decade(queryset, decades_grouping)
            if ratings_grouping:
                queryset = self.group_by_rating(queryset, ratings_grouping)
            date_from_grouping = self.form.cleaned_data['date_from']
            # When filtering, it is neccesary to add one day do 'date_to', to make this day inclusive
            # Otherwise, the last day showing would be te previous day of date_to_grouping
            date_to_grouping = self.form.cleaned_data['date_to']
            if date_from_grouping:
                if date_to_grouping:
                    queryset = queryset.filter(date_rated__range=[date_from_grouping, date_to_grouping+timedelta(days=1)])
                else:
                    queryset = queryset.filter(date_rated__gte=date_from_grouping)
            elif date_to_grouping:
                queryset = queryset.filter(date_rated__lte=date_to_grouping+timedelta(days=1))
            # Add form data to the context
            # (needed to keep sorting and grouping consistent across pagination)
            self.extra_context = self.form.cleaned_data
        else:
            decades_grouping = self.form.cleaned_data['group_by_decades']
            ratings_grouping = self.form.cleaned_data['group_by_ratings']
            if decades_grouping:
                queryset = self.group_by_decade(queryset, decades_grouping)
            if ratings_grouping:
                queryset = self.group_by_rating(queryset, ratings_grouping)
            self.extra_context = self.form.cleaned_data

        # GROUPING DONE, NOW SORT THE DATA THAT IS LEFT
        ordering = self.form.cleaned_data['sort_by']
        if ordering:
            if 'value' in ordering or 'date_rated' in ordering:
                return queryset.order_by(ordering)
            else:
                if ordering.startswith('-'):
                    return queryset.order_by(f'-movie__{ordering[1:]}')
                else:
                    return queryset.order_by(f'movie__{ordering}')
        else:
            return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_sorting_grouping'] = self.form
        context['profile_owner'] = self.profile_owner
        return context

class MoviesTable(tables.Table):
    # TODO: add custom styling for this column, and for header
    title = tables.LinkColumn("movie_detail", args=[A("pk")])
    class Meta:
        model = Movie
        template_name = 'recommender/bootstrap4_custom.html'

class MoviesListTableView(tables.SingleTableView):
    table_class = MoviesTable
    queryset = Movie.objects.all()
    paginate_by = 15
    template_name = 'recommender/movie_list_table.html'

class FilteredPersonListView(SingleTableMixin, FilterView):
    table_class = MoviesTable
    model = Movie
    template_name = 'recommender/movie_list_table.html'

    # TODO: add filtering by decades
    filterset_class = MovieFilter


class MoviesListView(ListView):
    model = Movie
    context_object_name = 'movies'
    paginate_by = 15
    ordering = 'id'

    def get_queryset(self):
        # queryset = super().get_queryset()
        queryset = Movie.objects.all()
        self.form = MovieSortGroupForm(self.request.GET)
        if self.form.is_valid():
            decades_grouping = self.form.cleaned_data['group_by_decades']
            if decades_grouping:
                upper_decades_limits = list(map(int, decades_grouping))
                movies_from_decades = queryset.filter(year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
                for limit in upper_decades_limits[1:]:
                    movies_from_decades |= queryset.filter(year_released__range=[(limit - 9), (limit)])
                queryset = movies_from_decades

        self.extra_context = self.form.cleaned_data
        ordering = self.form.cleaned_data['sort_by']
        if ordering:
            return queryset.order_by(ordering)
        else:
            return queryset.order_by(self.ordering)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_sorting_grouping'] = self.form
        return context

class UserListView(ListView):
    model = User
    context_object_name = 'users'
    paginate_by = 50
    template_name = 'recommender/user_list.html'


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
        context['actors'] = self.object.actors.all()
        context['genres'] = self.object.genres.all()
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
        if Rating.objects.filter(who_rated=self.request.user.id, movie_id=self.kwargs['pk']).exists():
            # Update view
            view = RatingUpdateView.as_view()
        else:
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
        form.instance.movie = self.movie_object
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
        movie_object = self.get_object().movie
        form.instance.movie = movie_object
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
    template_name = 'recommender/delete_rating.html'

    def get_object(self, *args, **kwargs):
        obj = super().get_object()
        print(f'obj:{obj}')
        new_obj = obj.rating_set.get(who_rated=self.request.user.id)
        print(f'new obj: {new_obj}')
        return new_obj

    def test_func(self):
        rating = self.get_object()
        print(f'test func: {rating}')
        if self.request.user == rating.who_rated:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'pk': self.kwargs['pk']})

class EstablishPreferencesView(ListView):
    # After user is created, select n(20? 30? 40?) movies to provide initial
    # recommendations for him

    model = Movie
    template_name = 'recommender/preferences.html'
    context_object_name = 'movies'

    def get_queryset(self):
        print('losu losu')
        # TODO: first draw top 400 most rated movies, then out of those 400,
        # draw n with the biggest variance in ratings
        # For testing: ensure that user has not rated any of these movies
        return Movie.objects.all().order_by('?')[:10]
        # return Movie.objects.all()[:10]

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)


def user_stats(request, username):
    active_user = User.objects.prefetch_related(
            Prefetch(
                'rating_set',
            )).get(username=username)
    users_ratings = active_user.rating_set.all()
    average_rating = round(users_ratings.aggregate(Avg('value'))['value__avg'], 2)
    no_of_ratings = users_ratings.count()
    ratings_distribution = []

    for i in range(10):
        ratings_distribution.append(users_ratings.filter(value=i+1).count())

    values = ratings_distribution
    desc = [f'{i}' for i in range(1, 11)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=desc,
                         y=values,
                         text=values,
                         textposition='auto',
                         hovertext=[f'Number of movies rated {i+1}' for i in range(10)]))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        xaxis=dict(
            tickmode='linear',
        )
    )

    plot_div = plot(fig, output_type='div', show_link=False, link_text="")

    rated_movies = Movie.objects.filter(rating__who_rated=2).prefetch_related('genres')

    all_genres = []
    for movie in rated_movies:
        # TODO: probably too slow, find way to make this more efficient
        all_genres += list(movie.genres.all().values_list('name', flat=True))

    genres_counter = Counter(all_genres)
    top_n_genres = (genres_counter.most_common(7))      # n = 7

    with_even_indices = top_n_genres[::2]
    with_odd_indices = top_n_genres[1::2]

    top_n_genres_shuffled = with_even_indices + with_odd_indices

    a,b,c = 1,2,3

    fig = go.Figure(data=go.Scatterpolar(
      r=[i[1] for i in top_n_genres_shuffled],
      theta=[i[0] for i in top_n_genres_shuffled],
      fill='toself',
    # hovertemplate = f"%{r}: <br>Popularity: %{b} </br> %{c}"

    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False
            ),
        ),
        showlegend=False
    )

    plot_div_genres = plot(fig, output_type='div', show_link=False, link_text="")

    context = {
        'active_user': active_user,
        'average_rating': average_rating,
        'ratings_distribution': ratings_distribution,
        'plot_div': plot_div,
        'plot_div_genres': plot_div_genres,
        'genres_counter': genres_counter,
        'no_of_ratings': no_of_ratings,
    }
    return render(request, 'recommender/stats.html', context)


def recommend(request, username):
    # Calculate similarity between user 2 and 3
    # TODO: use prefetch
    common_items = Movie.objects.filter(rating__who_rated=2) & Movie.objects.filter(rating__who_rated=3)
    licznik = sum((i.rating_set.get(who_rated=2).value*i.rating_set.get(who_rated=3).value) for i in common_items)
    print(licznik)
    mianownik = np.sqrt(sum(i.rating_set.get(who_rated=2).value**2 for i in common_items)*sum(i.rating_set.get(who_rated=3).value**2 for i in common_items))

    print(licznik/mianownik)


    context = {
        'username': username
    }
    return render(request, 'recommender/recommend.html', context)


def new_user(request):
    return render(request, 'recommender/new_user.html')

def users_list(request):
    return render(request, 'recommender/users_list.html')

def add_user(request):
    return render(request, 'recommender/add_user.html')
