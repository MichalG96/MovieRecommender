from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Movie(models.Model):
    movielens_id = models.IntegerField()
    # TODO: assign imdb_id and timdb_id automatically, based on Links model
    imdb_id = models.IntegerField()
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=200)
    year_released = models.IntegerField()
    director = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.movielens_id}_{self.title}'

class Rating(models.Model):
    movielens_id = models.ForeignKey(Movie,  on_delete=models.CASCADE)
    who_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    date_rated = models.DateTimeField(default=timezone.now())

    class Meta:
        constraints = [models.UniqueConstraint(fields=['movielens_id', 'who_rated'], name='No multiple ratings')]

    def __str__(self):
        return f'user_{self.who_rated}_movie_{self.movielens_id}'


