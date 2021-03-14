from django.shortcuts import render, redirect, get_object_or_404
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

from .forms import UserRegisterForm, UserRatingForm
from .models import Movie, Rating

from .filters import MovieFilter, RatingFilter, UserFilter
from .tables import RatingsTable, MoviesTable
from .recommendation_algorithms import ContentBased

# Third - party Django modules
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from plotly.offline import plot
import plotly.graph_objects as go
import requests
from collections import Counter

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

        queryset = self.profile_owner.rating_set.all().order_by('date_rated')
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
        genres = [genre_dict['name'] for genre_dict in r['genres']]
        overview = r['overview']
        img_url = f'{BASE_IMG_URL}{IMG_SIZE}{r["poster_path"]}'
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


class EstablishPreferencesView(ListView):
    # After user is created, select n(20? 30? 40?) movies to provide initial
    # recommendations for him
    model = Movie
    template_name = 'recommender/preferences.html'
    context_object_name = 'movies'

    def get_queryset(self):
        # TODO: first draw top 400 most rated movies, then out of those 400,
        #  draw n with the biggest variance in ratings
        #  For testing: ensure that user has not rated any of these movies

        movies_sorted_by_popularity = Movie.objects.all(). \
            annotate(no_of_ratings=Count('rating')). \
            order_by('-no_of_ratings')

        k = 400
        n = 40
        no_of_ratings_for_kth_movie = movies_sorted_by_popularity[k].no_of_ratings
        movies_with_std = movies_sorted_by_popularity.annotate(
            ratings_std=StdDev('rating__value'))

        popular_movies_with_high_std = movies_with_std.filter(
            no_of_ratings__gte=no_of_ratings_for_kth_movie).order_by('-ratings_std')[:n]

        return popular_movies_with_high_std

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.get_queryset())
        active_user = User.objects.prefetch_related(
            Prefetch(
                'rating_set',
            )).get(username=self.kwargs['username'])

        # print(vars(active_user))
        # print(active_user.rating_set.count())
        no_of_rated_movies = active_user.rating_set.count()

        context['no_of_rated_movies'] = no_of_rated_movies

        return context


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
                         hovertext=[f'Number of movies rated: {i + 1}' for i in range(10)]))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        xaxis=dict(
            tickmode='linear',
        )
    )

    # Generate HTML and JS for the plot
    plot_div_ratings_distribution = plot(fig, output_type='div', show_link=False, link_text="")

    rated_movies = Movie.objects.filter(rating__who_rated=active_user.id).prefetch_related('genres')
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

    content_based_recommendations = ContentBased(username)
    recommended_movies, predicted_ratings = content_based_recommendations.recommend_n_movies(20)
    context = {
        'username': username,
        'recommended_movies': zip(recommended_movies, predicted_ratings)
    }
    return render(request, 'recommender/recommend.html', context)


def new_user(request):
    return render(request, 'recommender/new_user.html')
