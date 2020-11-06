from .models import Movie, Rating

import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

class RatingsTable(tables.Table):
    # TODO: add custom styling for this column, and for header
    title = tables.LinkColumn("movie_detail", args=[A("movie__pk")], accessor='movie.title')
    director = tables.Column(accessor='movie.director')
    year_released = tables.Column(accessor='movie.year_released')
    movielens_id = tables.Column(accessor='movie.movielens_id')
    date_rated = tables.DateTimeColumn(format ='d/m/Y H:i:s')

    class Meta:
        model = Rating
        template_name = 'recommender/bootstrap4_custom.html'
        fields = ('movielens_id', 'title', 'director', 'year_released', 'value', 'date_rated')


class MoviesTable(tables.Table):
    # TODO: add custom styling for this column, and for header
    title = tables.LinkColumn("movie_detail", args=[A("pk")])
    class Meta:
        model = Movie
        template_name = 'recommender/bootstrap4_custom.html'
