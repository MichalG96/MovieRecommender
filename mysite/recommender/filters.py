from datetime import timedelta

from django import forms

from django_filters import MultipleChoiceFilter, FilterSet, CharFilter, DateFilter

from .models import Movie

# upper limits of decades: 1919, 1929, ..., 2029
decades_upper = ([1919 + 10 * i for i in range(12)])
# TODO: change text
decades_ranges = ['To 1919'] + [f"{1920 + 10 * i}'s" for i in range(11)]
DECADE_CHOICES = (tuple(zip(decades_upper, decades_ranges)))

class MovieFilter(FilterSet):

    year_released = MultipleChoiceFilter(choices=DECADE_CHOICES, widget=forms.CheckboxSelectMultiple(), method='get_movies_from_decades')

    def get_movies_from_decades(self, queryset, name, value):
        upper_decades_limits = list(map(int, value))
        movies_from_decades = queryset.filter(year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
        for limit in upper_decades_limits[1:]:
            movies_from_decades |= queryset.filter(year_released__range=[(limit - 9), (limit)])
        return movies_from_decades

    class Meta:
        model = Movie
        fields = {
            'title': ['icontains']
        }

class DateInput(forms.DateInput):
    input_type = 'date'

class RatingFilter(FilterSet):
    movie__title = CharFilter(lookup_expr='icontains')

    possible_ratings = [i for i in range(1, 11)]
    RATING_CHOICES = (tuple(zip(possible_ratings, possible_ratings)))

    value = MultipleChoiceFilter(choices=RATING_CHOICES, widget=forms.CheckboxSelectMultiple)
    movie__year_released = MultipleChoiceFilter(choices=DECADE_CHOICES, widget=forms.CheckboxSelectMultiple, method='get_movies_from_decades')

    date_from = DateFilter(field_name='date_rated', lookup_expr='gte', widget=DateInput())
    date_to = DateFilter(field_name='date_rated', widget=DateInput(), method='include_end_date_day')

    # When filtering, it is neccesary to add one day do 'date_to', to make this day inclusive
    # Otherwise, the last day showing would be the previous day
    def include_end_date_day(self, queryset, name, value):
        queryset = queryset.filter(date_rated__lte=value + timedelta(days=1))
        return queryset

    def get_movies_from_decades(self, queryset, name, value):
        upper_decades_limits = list(map(int, value))
        movies_from_decades = queryset.filter(movie__year_released__range=[(upper_decades_limits[0] - 9), (upper_decades_limits[0])])
        for limit in upper_decades_limits[1:]:
            movies_from_decades |= queryset.filter(movie__year_released__range=[(limit - 9), (limit)])
        return movies_from_decades

    # class Meta:

    #     model = Movie
    #     fields = {
    #         'movie__title': ['icontains']
    #     }

