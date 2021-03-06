import random
from collections import Counter

from plotly.offline import plot
import plotly.graph_objects as go
import requests
import pandas as pd

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Count, Max, Min, Prefetch, StdDev
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.views import LoginView

# Third - party Django modules
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from .forms import UserRegisterForm, UserRatingForm, EstablishPreferencesForm
from .models import Movie, Rating, TopMovie
from .filters import MovieFilter, RatingFilter, UserFilter
from .tables import RatingsTable, MoviesTable
from .recommendation_algorithms import ContentBased

BASE_TMDB_URL = 'https://api.themoviedb.org/3/movie/'
API_KEY = 'bef647566a5b4968a35cd34a79dc3dce'
BASE_IMG_URL = 'https://image.tmdb.org/t/p/'
# available sizes :"w92", "w154"," w185", "w342", "w500", "w780", "original"
IMG_SIZE = 'w185/'
IMG_SIZE_SMALL = 'w92/'


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('homepage')
    else:
        form = UserRegisterForm()
    return render(request, 'recommender/register.html', {'form': form})


class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        active_user_queryset = User.objects.filter(
            username=self.request.POST.get('username'))
        if active_user_queryset.exists():
            active_user = active_user_queryset.first()
            if active_user.last_login is None:
                self.request.session['first_login'] = True
            else:
                self.request.session['first_login'] = False
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        success_url = super().get_success_url()
        active_user = self.request.user
        if self.request.session['first_login']:
            return reverse('preferences', kwargs={'username': active_user.username})
        else:
            return success_url


# TODO: display warning when 'date to' is smaller than 'date from'
class FilteredRatingListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_class = RatingsTable
    model = Movie
    template_name = 'recommender/rating_list_table.html'
    paginate_by = 15
    filterset_class = RatingFilter

    def get_queryset(self):
        self.profile_owner = User.objects.prefetch_related(
            Prefetch(
                'rating_set',
            )).get(username=self.kwargs['username'])

        queryset = self.profile_owner.rating_set.all().order_by('-date_rated')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_owner'] = self.profile_owner
        return context


class FilteredMovieListView(SingleTableMixin, FilterView):
    table_class = MoviesTable
    model = Movie
    template_name = 'recommender/movie_list_table.html'
    paginate_by = 20
    ordering = 'id'
    filterset_class = MovieFilter


class UserListView(FilterView):
    model = User
    context_object_name = 'users'
    paginate_by = 25
    ordering = 'id'
    filterset_class = UserFilter
    template_name = 'recommender/user_list.html'


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'recommender/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tmdb_id = self.object.tmdb_id
        url = f'{BASE_TMDB_URL}{tmdb_id}?api_key={API_KEY}'
        url_credits = f'{BASE_TMDB_URL}{tmdb_id}/credits?api_key={API_KEY}'
        r = requests.get(url).json()
        print(r)
        if r.get('success') == False:
            return context
        genres = [genre_dict['name'] for genre_dict in r.get('genres')]
        overview = r.get('overview')
        img_url = f'{BASE_IMG_URL}{IMG_SIZE}{r.get("poster_path")}'
        r_credits = requests.get(url_credits).json()
        cast = [{'name': person['name'], 'character': person['character']} for person in
                r_credits['cast'][:8]]
        context['actors'] = self.object.actors.all()
        context['genres'] = self.object.genres.all()
        try:
            context['rating'] = self.object.rating_set.all().get(
                who_rated=self.request.user.id)
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
        if Rating.objects.filter(who_rated=self.request.user.id,
                                 movie_id=self.kwargs['pk']).exists():
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

    # Tell the view, that you do not want to modify the Movie object, but rather Rating
    # object related to this movie
    def get_object(self, *args, **kwargs):
        obj = super().get_object()
        # This should not throw MultipleObjectsReturned error, because there is
        # UniqueConstraint asserting that there is only one rating per movie-user pair,
        # nor should it throw ObjectDoesNotExist because this view is executed only when
        # the Rating object exists
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


def add_rating(request, username):
    all_movies = list(serializers.deserialize('json', request.session.get('movies')))
    which_movie_currently = (request.session.get('movie_count')['count'])
    current_movie = all_movies[which_movie_currently].object
    movies_left = request.session['movies_left']['number']

    # Not all movies were yet proposed, send AJAX data with the next movie to display
    if movies_left > 1:
        next_movie = all_movies[which_movie_currently + 1].object
        request.session['movie_count'] = {'count': which_movie_currently + 1}
        tmdb_id = next_movie.tmdb_id
        url = f'{BASE_TMDB_URL}{tmdb_id}?api_key={API_KEY}'
        r = requests.get(url).json()
        genres = [genre_dict['name'] for genre_dict in r['genres']]
        overview = r['overview']
        img_url = f'{BASE_IMG_URL}{IMG_SIZE}{r["poster_path"]}'
        data = {
            'pk': next_movie.pk,
            'title': next_movie.title,
            'genres': genres,
            'overview': overview,
            'img_url': img_url
        }
    # All movies were proposed, send AJAX data saying that the establishing prefereces process has ended
    else:
        data = {
            'done_msg': "Thank you, you've rated enough movies, you can now view your recommendations"
        }
    if 'value' in request.POST.keys():  # Handle form
        # Make sure that the username from the url matches the username who's making a request
        if username == request.user.username:
            Rating.objects.create(
                movie=current_movie,
                value=request.POST['value'],
                who_rated=User.objects.get(username=username)
            )
    movies_left = request.session['movies_left']['number']
    request.session['movies_left'] = {'number': movies_left - 1}
    return JsonResponse(data)


@login_required
def establish_preferences(request, username):
    modified_user = User.objects.prefetch_related(
        Prefetch(
            'rating_set',
        )).get(username=username)
    active_user_username = request.user.username
    if modified_user.username == active_user_username:

        # TODO: optimize this process, it can't be this slow
        # Get movies not rated by the user:
        rated_movies_id = list(
            modified_user.rating_set.all().values_list('movie', flat=True))
        not_rated_movies = Movie.objects.all().exclude(id__in=rated_movies_id)
        movies_sorted_by_popularity = not_rated_movies. \
            annotate(no_of_ratings=Count('rating'), ratings_std=StdDev('rating__value')). \
            order_by('-no_of_ratings')
        no_of_most_popular = 500
        no_of_movies_with_std = 100
        no_of_proposed_movies = 40
        no_of_ratings_for_kth_movie = movies_sorted_by_popularity[
            no_of_most_popular].no_of_ratings
        most_popular_movies = movies_sorted_by_popularity.filter(
            no_of_ratings__gte=no_of_ratings_for_kth_movie).order_by('-ratings_std')
        std_dev_of_nth_movie = most_popular_movies[no_of_movies_with_std].ratings_std
        popular_movies_with_high_std = most_popular_movies.filter(
            ratings_std__gte=std_dev_of_nth_movie)
        rand_indices = random.sample(
            list(popular_movies_with_high_std.values_list('id', flat=True)),
            no_of_proposed_movies)
        proposed_movies = popular_movies_with_high_std.filter(id__in=rand_indices)

        # no_of_proposed_movies = 10
        # no_of_movies = Movie.objects.all().count()
        # rand_indices = random.sample(range(no_of_movies), no_of_proposed_movies)
        # proposed_movies = Movie.objects.filter(id__in=rand_indices)

        first_movie = proposed_movies.first()
        tmdb_id = first_movie.tmdb_id
        url = f'{BASE_TMDB_URL}{tmdb_id}?api_key={API_KEY}'
        r = requests.get(url).json()
        overview = r['overview']
        img_url = f'{BASE_IMG_URL}{IMG_SIZE}{r["poster_path"]}'

        if request.session.get('first_login'):
            welcome_text = "Welcome! We present you a set of movies. Please rate the ones you've seen to help us establish your preferences"
            del (request.session['first_login'])
        else:
            welcome_text = ''

        context = {
            'form': EstablishPreferencesForm(),
            'movie': first_movie,
            'no_of_rated_movies': modified_user.rating_set.count(),
            'img_url': img_url,
            'overview': overview,
            'welcome_text': welcome_text,
        }

        # Pass movie ids to session
        request.session['movies'] = serializers.serialize("json", proposed_movies)
        # This variable points to which movie is currently being rated
        request.session['movie_count'] = {'count': 0}
        request.session['movies_left'] = {'number': no_of_proposed_movies}

        return render(request, 'recommender/preferences.html', context)

    else:
        return render(request, 'recommender/preferences_no_access.html',
                      {'username': active_user_username})


@login_required
def user_stats(request, username):
    # Get active user, use "Prefetch" to limit the number of database queries
    active_user = User.objects.prefetch_related(
        Prefetch(
            'rating_set',
        )).get(username=username)

    # Get basic user info
    users_ratings = active_user.rating_set.all()

    std_rating = round(users_ratings.aggregate(StdDev('value'))['value__stddev'], 2)
    average_rating = round(users_ratings.aggregate(Avg('value'))['value__avg'], 2)
    no_of_ratings = users_ratings.count()

    movies_ordered_by_rating = users_ratings.order_by('value')
    top_3 = movies_ordered_by_rating[::-1][:3]
    bottom_3 = movies_ordered_by_rating[:3]

    top_3_poster_urls, bottom_3_poster_urls = [], []

    for rating in top_3:
        url = f'{BASE_TMDB_URL}{rating.movie.tmdb_id}?api_key={API_KEY}'
        r = requests.get(url).json()
        top_3_poster_urls.append(f'{BASE_IMG_URL}{IMG_SIZE_SMALL}{r["poster_path"]}')

    for rating in bottom_3:
        url = f'{BASE_TMDB_URL}{rating.movie.tmdb_id}?api_key={API_KEY}'
        r = requests.get(url).json()
        bottom_3_poster_urls.append(f'{BASE_IMG_URL}{IMG_SIZE_SMALL}{r["poster_path"]}')

    # List containing the number of each rating given by the user; how many 1s, 2s, etc.
    ratings_distribution = [users_ratings.filter(value=i + 1).count() for i in range(10)]

    desc = [f'{i}' for i in range(1, 11)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=desc,
                         y=ratings_distribution,
                         text=ratings_distribution,
                         textposition='auto',
                         hovertext=[f'Number of movies rated: {i + 1}' for i in
                                    range(10)]))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        xaxis=dict(
            tickmode='linear',
        )
    )

    # Generate HTML and JS for the plot
    plot_div_ratings_distribution = plot(fig, output_type='div', show_link=False,
                                         link_text="")

    rated_movies = Movie.objects.filter(
        rating__who_rated=active_user.id).prefetch_related('genres')
    all_genres = []
    for movie in rated_movies:
        # TODO: probably too slow, find way to make this more efficient
        all_genres += list(movie.genres.all().values_list('name', flat=True))

    genres_counter = Counter(all_genres)
    n = 7
    top_n_genres = (genres_counter.most_common(n))
    top_n_genres_shuffled = []
    for i in range(n // 2):
        top_n_genres_shuffled.append(top_n_genres[i])
        top_n_genres_shuffled.append(top_n_genres[-i - 1])
    if n % 2 != 0:
        top_n_genres_shuffled.append(top_n_genres[n // 2])

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
        'std_rating': std_rating,
        'ratings_distribution': ratings_distribution,
        'plot_div_ratings_distribution': plot_div_ratings_distribution,
        'plot_div_genres': plot_div_genres,
        'genres_counter': genres_counter,
        'no_of_ratings': no_of_ratings,
        'top_3_poster_urls': top_3_poster_urls,
        'bottom_3_poster_urls': bottom_3_poster_urls
    }
    return render(request, 'recommender/stats.html', context)


@login_required
def recommend(request, username):
    # If the user hasn't got enough ratings - redirect to EstablishPreferences View

    # Calculate similarity between user 2 and 3
    # TODO: use prefetch
    # common_items = Movie.objects.filter(rating__who_rated=2) & Movie.objects.filter(rating__who_rated=3)
    # licznik = sum((i.rating_set.get(who_rated=2).value*i.rating_set.get(who_rated=3).value) for i in common_items)
    # print(licznik)
    # mianownik = np.sqrt(sum(i.rating_set.get(who_rated=2).value**2 for i in common_items)*sum(i.rating_set.get(who_rated=3).value**2 for i in common_items))
    # print(licznik/mianownik)

    # TODO: after recommending, add movies to the database.
    # If there are recommended movies in the database - display them. If not - perform recommendation
    #
    content_based_recommendations = ContentBased(username)
    recommended_movies, predicted_ratings = content_based_recommendations.recommend_n_movies(
        20)

    # ratings_df = pd.DataFrame(columns=['user', 'item', 'rating'])
    # all_ratings = Rating.objects.all()
    # for rating in all_ratings:
    #     ratings_df = ratings_df.append({
    #         'user': rating.who_rated_id,
    #         'item': rating.movie_id,
    #         'rating': rating.value,
    #     }, ignore_index=True)
    #
    # ratings_df.to_csv('static/ratings.csv')

    # for movie, rating in zip(recommended_movies, predicted_ratings):
    #     TopMovie.objects.create(user=request.user, movie=movie, predicted_value=rating)

    context = {
        'username': username,
        'recommended_movies': zip(recommended_movies, predicted_ratings)
    }
    return render(request, 'recommender/recommend.html', context)


def new_user(request):
    return render(request, 'recommender/new_user.html')
