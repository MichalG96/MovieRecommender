from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Rating(models.Model):
    movielens_id = models.IntegerField()    # change to foreign key of Movie
    who_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    date_rated = models.DateTimeField(default=timezone.now())


    def __str__(self):
        return f'movie_{self.movielens_id}_{self.who_rated}'
