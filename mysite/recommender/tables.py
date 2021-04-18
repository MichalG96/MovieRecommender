from .models import Movie, Rating

import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor


class RatingsTable(tables.Table):
    # TODO: add custom styling for this column, and for header
    title = tables.LinkColumn("movie_detail", args=[A("movie__pk")],
                              accessor='movie.title',
                              attrs={
                                  "a": {"class": "link-glow"},
                                  "td": {"class": "link-glow"},
                                  "th": {"style": "width: 22%"}
                              })
    director = tables.Column(accessor='movie.director',
                             attrs={
                                 "td": {
                                     "class": "row-glow"},
                                 "th": {
                                     "style": "width: 13%"
                                 }
                             }
                             )
    year_released = tables.Column(accessor='movie.year_released',
                                  attrs={
                                      "td": {
                                          "class": "row-glow center-column"
                                      },
                                      "th": {
                                          "class": "center-column",
                                          "style": "width: 9%"
                                      }
                                  })
    movielens_id = tables.Column(accessor='movie.movielens_id',
                                 attrs={
                                     "td": {
                                         "class":
                                             "row-glow center-column"
                                     },
                                     "th": {
                                         "class": "center-column",
                                         "style": "width: 14%"
                                     }})
    date_rated = tables.DateTimeColumn(format='d/m/Y H:i:s',
                                       attrs={
                                           "td": {
                                               "class": "row-glow center-column"
                                           },
                                           "th": {
                                               "class": "center-column",
                                               "style": "width: 16%"
                                           }})
    value = tables.Column(
        attrs={"td": {"class": "row-glow center-column bold-col"},
               "th": {"class": "center-column", "style": "width: 10%"}})

    class Meta:
        model = Rating
        template_name = 'recommender/bootstrap4_custom.html'
        attrs = {"class": "custom-table"}
        row_attrs = {
            "class": "table-row"
        }
        fields = (
            'movielens_id', 'title', 'director', 'year_released', 'value',
            'date_rated')


class MoviesTable(tables.Table):
    # TODO: add custom styling for this column, and for header

    id = tables.Column(attrs={"td": {"class": "row-glow center-column"},
                              "th": {"class": "center-column",
                                     "style": "width: 7%"}})
    movielens_id = tables.Column(
        attrs={"td": {"class": "row-glow center-column"},
               "th": {"class": "center-column", "style": "width: 15%"}})
    imdb_id = tables.Column(attrs={"td": {"class": "row-glow center-column"},
                                   "th": {"class": "center-column",
                                          "style": "width: 11%"}})
    tmdb_id = tables.Column(attrs={"td": {"class": "row-glow center-column"},
                                   "th": {"class": "center-column",
                                          "style": "width: 12%"}})
    title = tables.LinkColumn("movie_detail", args=[A("pk")],
                              attrs={"a": {"class": "link-glow"},
                                     "td": {"class": "link-glow"},
                                     "th": {"style": "width: 28%"}})
    year_released = tables.Column(
        attrs={"td": {"class": "row-glow center-column"},
               "th": {"class": "center-column", "style": "width: 8%"}})
    director = tables.Column(
        attrs={"td": {"class": "row-glow"}, "th": {"style": "width: 13%"}})

    class Meta:
        model = Movie
        attrs = {"class": "custom-table"}
        row_attrs = {
            "class": "table-row"
        }
        template_name = 'recommender/bootstrap4_custom.html'
