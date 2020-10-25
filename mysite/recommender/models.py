from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

class Genre(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

# https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_many/
# TODO: when using Postgres, try List field, or JSON field
class Actor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    movielens_id = models.IntegerField()
    imdb_id = models.IntegerField()
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=200)
    year_released = models.IntegerField()
    director = models.CharField(max_length=100)
    genres = models.ManyToManyField(Genre)
    actors = models.ManyToManyField(Actor)

    def __str__(self):
        return f'MovieLens_id_{self.movielens_id}_Movie_id_{self.id}_{self.title}'

    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'pk': self.pk})


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    who_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    date_rated = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['movie', 'who_rated'], name='No multiple ratings')]
        # Equivalent:
        # unique_together = [['movie', 'who_rated']]

    def __str__(self):
        return f'user_{self.who_rated.pk}_movie_{self.movie}_value_{self.value}'

