from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Movie(models.Model):
    movielens_id = models.IntegerField()
    imdb_id = models.IntegerField()
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=200)
    year_released = models.IntegerField()
    director = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.movielens_id}_{self.title}'


class Rating(models.Model):
    movielens_id = models.ForeignKey(Movie, on_delete=models.CASCADE)    # change to foreign key of Movie
    who_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    date_rated = models.DateTimeField(default=timezone.now())


    def __str__(self):
        return f'user_{self.who_rated}_movie_{self.movielens_id}'


