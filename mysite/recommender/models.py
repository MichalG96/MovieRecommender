from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse


# TODO: assign movielens Id automatically on registration
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    movielens_id = models.IntegerField()

    def __str__(self):
        return f'{self.user.username}_movielens_id_{self.movielens_id}'


class Genre(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    movielens_id = models.IntegerField(verbose_name='movielens ID')
    imdb_id = models.IntegerField(verbose_name='iMdB ID')
    tmdb_id = models.IntegerField(verbose_name='tMdB ID')
    title = models.CharField(max_length=200)
    year_released = models.IntegerField(verbose_name='year')
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
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),
                                                         MaxValueValidator(10)],
                                             verbose_name='rating')
    date_rated = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['movie', 'who_rated'], name='No multiple ratings')]
        # Equivalent:
        # unique_together = [['movie', 'who_rated']]

    def __str__(self):
        return f'user_{self.who_rated.pk}_movie_{self.movie}_value_{self.value}'


class TopMovie(models.Model):
    # Stores 100 top movies for each user
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predicted_value = models.FloatField()
    date_predicted = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['movie', 'user'], name='No multiple predicted ratings')]

    def __str__(self):
        return f'user_{self.user.pk}_movie_{self.movie}_predicted_value_{self.predicted_value}'
