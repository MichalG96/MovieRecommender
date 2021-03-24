from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML
from crispy_forms.bootstrap import InlineCheckboxes

from .models import Rating


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


SORTING_OPTIONS = (
    ('id', 'ID \u25B2'),
    ('-id', 'ID \u25BC'),
    ('imdb_id', 'IMDb ID \u25B2'),
    ('-imdb_id', 'IMDb ID \u25BC'),
    ('tmdb_id', 'tMDb ID \u25B2'),
    ('-tmdb_id', 'tMDb ID \u25BC'),
    ('title', 'Title \u25B2'),
    ('-title', 'Title \u25BC'),
    ('year_released', 'Year of release \u25B2'),
    ('-year_released', 'Year of release \u25BC'))

decades_upper = ([1889 + 10 * i for i in range(15)])
decades_ranges = ['- 1889'] + [f'{1890 + 10 * i} - {1899 + 10 * i}' for i in range(14)]
DECADE_CHOICES = (tuple(zip(decades_upper, decades_ranges)))


class MovieSortGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'first arg is the legend of the fieldset',
                'group_by_decades',
                'sort_by',
            ),
            HTML("""
                       <p>We use notes to get better, <strong>please help us {{ username }}</strong></p>
                   """),

            InlineCheckboxes('group_by_decades')
        )

        self.fields['sort_by'].label = 'Sort by:'

    sort_by = forms.ChoiceField(choices=SORTING_OPTIONS, required=False)
    # widget=forms.Select(attrs={'onclick': "alert('foo !');"}))
    group_by_decades = forms.MultipleChoiceField(choices=DECADE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)


class MovieRatingSortGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sort_by'].label = 'Sort by:'

    SORTING_OPTIONS = SORTING_OPTIONS[:2] + SORTING_OPTIONS[6:] + (
        ('value', 'Rating \u25B2'),
        ('-value', 'Rating \u25BC'),
        ('date_rated', 'Date rated \u25B2'),
        ('-date_rated', 'Date rated \u25BC'))
    possible_ratings = [i for i in range(1, 11)]
    RATING_CHOICES = (tuple(zip(possible_ratings, possible_ratings)))

    sort_by = forms.ChoiceField(choices=SORTING_OPTIONS, required=False)
    group_by_ratings = forms.MultipleChoiceField(choices=RATING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    group_by_decades = forms.MultipleChoiceField(choices=DECADE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    # TODO: date picker
    date_from = forms.DateField(widget=forms.SelectDateWidget, required=False)
    date_to = forms.DateField(widget=forms.SelectDateWidget, required=False)

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_from > date_to:
                msg = "'Date from' cannot be later than 'Date to"
                self.add_error('date_from', msg)
                raise ValidationError(
                    "'Date from' cannot be later than 'Date to"
                )


class EstablishPreferencesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EstablishPreferencesForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget.attrs['min'] = 1
        self.fields['value'].widget.attrs['max'] = 10

    class Meta:
        model = Rating
        fields = ('value',)
        labels = {
                "value": False
            }