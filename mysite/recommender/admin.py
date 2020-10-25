from django.contrib import admin
from .models import Rating, Movie, Genre, Actor

admin.site.register(Rating)
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Actor)
