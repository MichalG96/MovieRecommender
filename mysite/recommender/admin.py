from django.contrib import admin
from .models import Rating, Movie, Genre, Actor, Profile, TopMovie
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('id', 'username', 'email', 'date_joined', 'last_login', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Rating)
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(TopMovie)
