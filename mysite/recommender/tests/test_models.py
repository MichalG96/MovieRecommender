from django.test import TestCase
from recommender.models import Movie, Actor, Genre, Rating


class MovieModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        genre1 = Genre(name='Adventure')
        genre2 = Genre(name='Animation')
        genre3 = Genre(name='Children')
        genre4 = Genre(name='Comedy')
        actor1 = Actor(name='Don Rickles')
        actor2 = Actor(name='Jim Varney')
        actor3 = Actor(name='Tim Allen')
        actor4 = Actor(name='Tom Hanks')
        for i in [genre1, genre2, genre3, genre4, actor1, actor2, actor3, actor4]:
            i.save()
        movie_for_testing = Movie(
            movielens_id=1,
            imdb_id=114709,
            tmdb_id=862,
            title='Toy Story',
            year_released=1995,
            director='John Lasseter',
        )
        movie_for_testing.save()
        movie_for_testing.genres.add(genre1, genre2, genre3, genre4)
        movie_for_testing.actors.add(actor1, actor2, actor3, actor4)

    def test_movielens_id_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('movielens_id').verbose_name
        self.assertEqual(field_label, 'movielens ID')

    def test_imdb_id_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('imdb_id').verbose_name
        self.assertEqual(field_label, 'iMdB ID')

    def test_tmdb_id_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('tmdb_id').verbose_name
        self.assertEqual(field_label, 'tMdB ID')

    def test_title_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_year_released_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('year_released').verbose_name
        self.assertEqual(field_label, 'year')

    def test_director_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('director').verbose_name
        self.assertEqual(field_label, 'director')

    def test_genres_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('genres').verbose_name
        self.assertEqual(field_label, 'genres')

    def test_actors_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field('actors').verbose_name
        self.assertEqual(field_label, 'actors')

    def test_title_max_length(self):
        movie = Movie.objects.get(id=1)
        max_length = movie._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_director_max_length(self):
        movie = Movie.objects.get(id=1)
        max_length = movie._meta.get_field('director').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_formatted_correctly(self):
        movie = Movie.objects.get(id=1)
        expected_object_name = f'MovieLens_id_{movie.movielens_id}_Movie_id_{movie.id}_{movie.title}'
        self.assertEqual(expected_object_name, str(movie))

    def test_get_absolute_url(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.get_absolute_url(), '/movie/1/')


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='Adventure')

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_object_name_is_formatted_correctly(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEqual(expected_object_name, str(genre))


class ActorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Actor.objects.create(name='Tom Hanks')

    def test_name_label(self):
        actor = Actor.objects.get(id=1)
        field_label = actor._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_object_name_is_formatted_correctly(self):
        actor = Actor.objects.get(id=1)
        expected_object_name = actor.name
        self.assertEqual(expected_object_name, str(actor))