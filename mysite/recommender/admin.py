from django.contrib import admin
from .models import Rating, Movie, Genre, MovieGenre, Actor, MovieActor
# Register your models here.

admin.site.register(Rating)
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(MovieGenre)
admin.site.register(Actor)
admin.site.register(MovieActor)
