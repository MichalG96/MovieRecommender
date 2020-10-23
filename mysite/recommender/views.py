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
from .forms import UserRatingForm, MovieSortGroupForm, MovieRatingSortGroupForm
from django.utils.datastructures import MultiValueDictKeyError
import requests
from datetime import timedelta

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
    ordering = '-date_rated'

    # Filter query so that it only returns current user's ratings
    def get_queryset(self):
        queryset = self.request.user.rating_set.all()
        self.form = MovieRatingSortGroupForm(self.request.GET)
        print(f'valid? {self.form.is_valid()}')
        print(self.form.cleaned_data)
        decades_grouping = self.form.cleaned_data['group_by_decades']
        ratings_grouping = self.form.cleaned_data['group_by_ratings']

        if decades_grouping:
            upper_decades_limits = list(map(int, decades_grouping))
            movies_from_decades = queryset.filter(movielens_id__year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
            for limit in upper_decades_limits[1:]:
                movies_from_decades |= queryset.filter(movielens_id__year_released__range=[(limit - 9), (limit)])
            # Consists only of movies from decades defined by the user
            queryset = movies_from_decades

        if ratings_grouping:
            possible_ratings = list(map(int, ratings_grouping))
            movies_with_ratings = queryset.filter(value=possible_ratings[0])
            for rating in possible_ratings[1:]:
                movies_with_ratings |= queryset.filter(value=rating)
            # Consists only of movies from decades and with ratings defined by the user
            queryset = movies_with_ratings

        # TODO: add validation: date_from can't be later than date_to
        if self.form.is_valid():
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

        # Add form data to the context (needed to keep sorting and grouping
        # consistent across pagination
        self.extra_context = self.form.cleaned_data

        # GROUPING DONE, NOW SORT THE DATA THAT IS LEFT
        ordering = self.form.cleaned_data['sort_by']
        print(ordering)
        if ordering:
            if 'value' in ordering or 'date_rated' in ordering:
                return queryset.order_by(ordering)
            else:
                if ordering.startswith('-'):
                    return queryset.order_by(f'-movielens_id__{self.get_ordering()[1:]}')
                else:
                    return queryset.order_by(f'movielens_id__{self.get_ordering()}')
        else:
            return queryset


    # def get_grouping(self):
    #     print('get_grouping')
    #
    #     #loop over this dict
    #     # print(self.request.GET.dict())
    #     # print(self.request.GET)
    #     if self.request.GET.__contains__('group_by_decades'):
    #     # if 'group_by_decades' in self.sorting_grouping_data: - ZLE, KLUCZE ZAWSZE SA, SPRAWDZAJ, CZY ZAWIERAJA WARTOSCI
    #         decades = list(map(int, self.request.GET.getlist('group_by_decades')))
    #         self.extra_context = {'group_by_decades': decades}
    #         # add to dict instead of returning
    #         return decades
    #     if self.request.GET.__contains__('group_by_ratings'):
    #         ratings = list(map(int, self.request.GET.getlist('group_by_ratings')))
    #
    #     if self.request.GET.__contains__('group_by_ratings'):
    #                 ratings = list(map(int, self.request.GET.getlist('group_by_ratings')))
    #     else:
    #         return None
    def get_ordering(self):
        print('get_ordering executing?')

        if self.request.GET.__contains__('sort_by'):
            ordering = self.request.GET['sort_by']
        else:
            ordering = super().get_ordering()
        return ordering

    def get_context_data(self, *, object_list=None, **kwargs):
        print('get context data')
        context = super().get_context_data(**kwargs)
        context['form_sorting_grouping'] = self.form
        return context

# TODO: redo all of this using data from from rather then separate GET requests
# maybe just rating list view
class MoviesListView(ListView):
    model = Movie
    context_object_name = 'movies'
    paginate_by = 15
    ordering = 'id'

    def get_queryset(self):
        self.form = MovieSortGroupForm(self.request.GET)
        queryset = super().get_queryset()
        upper_decades_limits = self.get_grouping()
        if upper_decades_limits:
            movies_from_decades = queryset.filter(movielens_id__year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
            for limit in upper_decades_limits[1:]:
                movies_from_decades |= queryset.filter(movielens_id__year_released__range=[(limit - 9), (limit)])
            return movies_from_decades
        else:
            return queryset

    def get_grouping(self):
        # If request.GET contains 'group_by_decades', sorting-grouping form has been used
        # (otherwise, QueryDict will be empty, or it will contain only 'sort_by' and 'page'
        if self.request.GET.__contains__('group_by_decades'):
            decades = list(map(int, self.request.GET.getlist('group_by_decades')))
            self.extra_context = {'group_by_decades': decades}
            return decades
        else:
            return None

    def get_ordering(self):
        if self.request.GET.__contains__('sort_by'):
            ordering = self.request.GET['sort_by']
            return ordering
        else:
            return super().get_ordering()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['form_sorting_grouping'] = MovieSortGroupForm(self.request.GET)
        context['form_sorting_grouping'] = self.form
        # można to przenieść do get queryset za pomoca extra context
        context['sort_by'] = self.get_ordering()
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
