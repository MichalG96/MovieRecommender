from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
# Create your models here.

class Movie(models.Model):
    movielens_id = models.IntegerField(unique=True)
    # TODO: assign imdb_id and timdb_id automatically, based on Links model
    imdb_id = models.IntegerField()
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=200)
    year_released = models.IntegerField()
    director = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.movielens_id}_{self.title}'

    # def get_absolute_url(self):
    #     return reverse('movie_detail', kwargs={'pk': self.pk})

class Rating(models.Model):
    movielens_id = models.ForeignKey(Movie, to_field='movielens_id', on_delete=models.CASCADE)
    who_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    date_rated = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['movielens_id', 'who_rated'], name='No multiple ratings')]

    def __str__(self):
        return f'user_{self.who_rated}_movie_{self.movielens_id}'

class Genre(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Actor(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


# Junction tables that store one row for each distinct ID of the Movie object and the ID of the Genre/Actor.
# Existence of such a row means the genre/actor is in that list for the Movie.
# TODO: when using Postgres, try List field, or JSON field

class MovieGenre(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'movie_{self.movie_id}_genre_{self.genre}'

class MovieActor(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'movie_{self.movie_id}_actor_{self.actor}'
