from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from recommender.models import Movie, Genre, Actor, Rating
from recommender.views import FilteredMovieListView

# fixtures = ['movies_test.json', 'actors.json', 'genres.json', 'users_test.json', 'ratings_test.json']


class HomepageViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/homepage.html')


class FilteredMovieListViewTest(TestCase):
    fixtures = ['actors.json', 'genres.json', 'movies_for_testing_FilteredMovieListView.json']

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/all_movies/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('all_movies'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('all_movies'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/movie_list_table.html')

    def test_pagination_is_20(self):
        response = self.client.get(reverse('all_movies'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        # Assert that the response is paginated
        self.assertTrue(response.context['is_paginated'] == True)
        # Assert that there are 20 objects on each page
        self.assertTrue(len(response.context['object_list']) == 20)

    def test_lists_all_movies(self):
        # Get third page and confirm it has (exactly) remaining 10 items
        response = self.client.get(reverse('all_movies') + '?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['object_list']) == 10)




# Old tests

# class MovieGroupingTestCase(TestCase):
#     fixtures = fixtures
#
#     def test_grouping_when_no_movies_exist(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1909')
#         self.assertFalse(response.context['object_list'].exists())
#
#     def test_grouping_movies_from_20s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1929')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1920, 1929])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_30s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1939')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1930, 1939])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_40s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1949')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1940, 1949])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_50s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1959')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1950, 1959])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_60s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1969')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1960, 1969])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_70s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1979')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1970, 1979])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_80s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1989')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1980, 1989])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_90s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=1999')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1990, 1999])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_2000s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=2009')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[2000, 2009])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_2010s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=2019')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[2010, 2019])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     def test_grouping_movies_from_2020s(self):
#         response = self.client.get('/all_movies/?sort_by=id&group_by_decades=2029')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[2020, 2029])
#         # Testing grouping only, igoring ordering
#         self.assertEqual(set(received_movies), set(movies_from_this_decade))
#
#     # TODO: group by multiple decades
#
# class MovieSortingTestCase(TestCase):
#     fixtures = fixtures
#     paginate_by = MoviesListView.paginate_by
#
#     def test_sorting_by_id_ascending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=id')
#         # print(response.context.keys())
#         # print(response.context['movies'])
#         # print(self.paginate_by)
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('id')
#
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_id_descending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=-id')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('-id')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_imdb_id_ascending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=imdb_id')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('imdb_id')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_imdb_id_descending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=-imdb_id')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('-imdb_id')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_tmdb_id_ascending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=tmdb_id')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('tmdb_id')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_tmdb_id_descending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=-tmdb_id')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('-tmdb_id')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_title_ascending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=title')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('title')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_title_descending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=-title')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('-title')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_year_released_ascending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=year_released')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('year_released')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_year_released_descending_returns_correct_queryset(self):
#         response = self.client.get('/all_movies/?sort_by=-year_released')
#         received_movies = response.context['paginator'].object_list
#         sorted_movies = Movie.objects.all().order_by('-year_released')
#         self.assertEqual(set(received_movies), set(sorted_movies))
#
#     def test_sorting_by_id_ascending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=id')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_greater_than_previous = True     # Attribute being id in this case
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.id < next_movie.id:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_greater_than_previous = False
#                 break
#         self.assertTrue(next_attribute_greater_than_previous)
#
#     def test_sorting_by_id_descending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=-id')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_less_than_previous = True
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.id > next_movie.id:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_less_than_previous = False
#                 break
#         self.assertTrue(next_attribute_less_than_previous)
#
#     def test_sorting_by_imdb_id_ascending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=imdb_id')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_greater_than_previous = True  # Attribute being id in this case
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.imdb_id < next_movie.imdb_id:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_greater_than_previous = False
#                 break
#         self.assertTrue(next_attribute_greater_than_previous)
#
#     def test_sorting_by_imdb_id_descending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=-imdb_id')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_less_than_previous = True
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.imdb_id > next_movie.imdb_id:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_less_than_previous = False
#                 break
#         self.assertTrue(next_attribute_less_than_previous)
#
#     def test_sorting_by_tmdb_id_ascending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=tmdb_id')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_greater_than_previous = True  # Attribute being id in this case
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.tmdb_id < next_movie.tmdb_id:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_greater_than_previous = False
#                 break
#         self.assertTrue(next_attribute_greater_than_previous)
#
#     def test_sorting_by_tmdb_id_descending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=-tmdb_id')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_less_than_previous = True
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.tmdb_id > next_movie.tmdb_id:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_less_than_previous = False
#                 break
#         self.assertTrue(next_attribute_less_than_previous)
#
#     def test_sorting_by_title_ascending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=title')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_greater_than_previous = True  # Attribute being id in this case
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.title < next_movie.title:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_greater_than_previous = False
#                 break
#         self.assertTrue(next_attribute_greater_than_previous)
#
#     def test_sorting_by_title_descending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=-title')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_less_than_previous = True
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.title > next_movie.title:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_less_than_previous = False
#                 break
#         self.assertTrue(next_attribute_less_than_previous)
#
#     def test_sorting_by_year_released_ascending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=year_released')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_greater_than_previous = True  # Attribute being id in this case
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.year_released <= next_movie.year_released:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_greater_than_previous = False
#                 break
#         self.assertTrue(next_attribute_greater_than_previous)
#
#     def test_sorting_by_year_released_descending_movies_in_correct_order(self):
#         # Checking for first page only
#         response = self.client.get('/all_movies/?sort_by=-year_released')
#         received_movies = response.context['paginator'].object_list
#         next_attribute_less_than_previous = True
#         # Check if movies are correctly sorted
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.year_released >= next_movie.year_released:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_less_than_previous = False
#                 break
#         self.assertTrue(next_attribute_less_than_previous)
#
#
# class MovieSortingGroupingTestCase(TestCase):
#     fixtures = fixtures
#
#     def test_sorting_with_grouping_together(self):
#         response = self.client.get('/all_movies/?sort_by=title&group_by_decades=1999')
#         received_movies = response.context['paginator'].object_list
#         movies_from_this_decade = Movie.objects.filter(year_released__range=[1990, 1999])
#         correct_movies_are_returned = set(received_movies) == set(movies_from_this_decade)
#         next_attribute_greater_than_previous = True
#             # Check if movies are correctly sorted in ascending order by title
#         prev_movie = received_movies[0]
#         for next_movie in received_movies[1:]:
#             if prev_movie.title < next_movie.title:
#                 prev_movie = next_movie
#             else:
#                 next_attribute_greater_than_previous = False
#                 break
#         self.assertTrue(correct_movies_are_returned and next_attribute_greater_than_previous)
#
