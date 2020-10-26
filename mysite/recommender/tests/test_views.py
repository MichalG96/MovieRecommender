from django.test import TestCase
from recommender.models import Movie

# Testing MovieListView

fixtures = ['movies_test.json', 'actors.json', 'genres.json']


class MovieGroupingTestCase(TestCase):
    fixtures = fixtures

    def test_grouping_when_no_movies_exist(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1909')
        self.assertFalse(response.context['object_list'].exists())

    def test_grouping_movies_from_20s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1929')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1920, 1929])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_30s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1939')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1930, 1939])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_40s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1949')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1940, 1949])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_50s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1959')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1950, 1959])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_60s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1969')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1960, 1969])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_70s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1979')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1970, 1979])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_80s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1989')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1980, 1989])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_90s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1999')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[1990, 1999])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_2000s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=2009')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[2000, 2009])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_2010s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=2019')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[2010, 2019])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

    def test_grouping_movies_from_2020s(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=2029')
        received_movies = response.context['object_list']
        movies_from_this_decade = Movie.objects.filter(year_released__range=[2020, 2029])
        # Testing grouping only, igoring ordering
        self.assertEqual(set(received_movies), set(movies_from_this_decade))

