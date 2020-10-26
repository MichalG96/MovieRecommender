from django.test import TestCase
from recommender.models import Movie, Actor, Genre, Rating

class MovieTestCase(TestCase):
    # fixtures = ['movies_test.json']

    def test1(self):
        response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1909&group_by_decades=1919&group_by_decades=1929')
        self.assertEqual(response.status_code, 200)