from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Rating
from django.forms.widgets import NumberInput

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserRatingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRatingForm, self).__init__(*args, **kwargs)
        # Overriding default field attributes
        self.fields['value'].widget.attrs['min'] = 1
        self.fields['value'].widget.attrs['max'] = 10

    class Meta:
        model = Rating
        fields = ['value']
        labels = {
            'value': '',
        }

SORTING_OPTIONS= (
    ('id', ''),
    ('-id', 'ID, descending'),
    ('imdb_id', 'IMDb ID, ascending'),
    ('-imdb_id', 'IMDb ID, descending'),
    ('tmdb_id', 'tMDb ID, ascending'),
    ('-tmdb_id', 'tMDb ID, descending'),
    ('title', 'Title, ascending'),
    ('-title', 'Title, descending'),
    ('year_released', 'Year of release, ascending'),
    ('-year_released', 'Year of release, descending'))

class MovieSortForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sort_by'].label = 'Sort by:'

    sort_by = forms.ChoiceField(choices=SORTING_OPTIONS, required=False)
                                      # widget=forms.Select(attrs={'onclick': "alert('foo !');"}))

class MovieRatingSortForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sort_by'].label = 'Sort by:'


    SORTING_OPTIONS = SORTING_OPTIONS[:2] + SORTING_OPTIONS[6:] + (
    ('value', 'Rating, ascending'),
    ('-value', 'Rating, descending'),
    ('date_rated', 'Date rated, ascending'),
    ('-date_rated', 'Date rated, descending'))

    sort_by = forms.ChoiceField(choices=SORTING_OPTIONS, required=False)

