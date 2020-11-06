from django import forms

from django_filters import MultipleChoiceFilter, FilterSet, CharFilter, NumberFilter

from .models import Movie

class MovieFilter(FilterSet):
    # TODO: separate filter for search by title
    title = CharFilter(lookup_expr='icontains')

    decades_upper = ([1889 + 10 * i for i in range(15)])
    decades_ranges = ['- 1889'] + [f'{1890 + 10 * i} - {1899 + 10 * i}' for i in range(14)]
    DECADE_CHOICES = (tuple(zip(decades_upper, decades_ranges)))

    imdb_id = NumberFilter()
    year_released = MultipleChoiceFilter(choices=DECADE_CHOICES, widget=forms.CheckboxSelectMultiple, method='get_movies_from_decades')

    def get_movies_from_decades(self, queryset, name, value):
        upper_decades_limits = list(map(int, value))
        movies_from_decades = queryset.filter(
            year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
        for limit in upper_decades_limits[1:]:
            movies_from_decades |= queryset.filter(year_released__range=[(limit - 9), (limit)])
        return movies_from_decades

    class Meta:
        model = Movie
        fields = {
            'tmdb_id': ['lt']
        }

class RatingFilter(FilterSet):
    # TODO: separate filter for search by title
    movie__title = CharFilter(lookup_expr='icontains')

    decades_upper = ([1889 + 10 * i for i in range(15)])
    decades_ranges = ['- 1889'] + [f'{1890 + 10 * i} - {1899 + 10 * i}' for i in range(14)]
    DECADE_CHOICES = (tuple(zip(decades_upper, decades_ranges)))

    possible_ratings = [i for i in range(1, 11)]
    RATING_CHOICES = (tuple(zip(possible_ratings, possible_ratings)))

    value = MultipleChoiceFilter(choices=RATING_CHOICES, widget=forms.CheckboxSelectMultiple)
    movie__year_released = MultipleChoiceFilter(choices=DECADE_CHOICES, widget=forms.CheckboxSelectMultiple, method='get_movies_from_decades')

    def get_movies_from_decades(self, queryset, name, value):
        upper_decades_limits = list(map(int, value))
        movies_from_decades = queryset.filter(movie__year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
        for limit in upper_decades_limits[1:]:
            movies_from_decades |= queryset.filter(movie__year_released__range=[(limit - 9), (limit)])
        return movies_from_decades

    class Meta:
        model = Movie
        fields = {
            'tmdb_id': ['lt']
        }

