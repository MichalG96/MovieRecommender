import datetime

from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from recommender.models import Movie, Genre, Actor, Rating
from recommender.views import FilteredMovieListView

from bs4 import BeautifulSoup

# fixtures = ['movies_test.json', 'actors.json', 'genres.json', 'users_test.json', 'ratings_test.json']


class HomepageViewTest(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/homepage.html')

    def test_username_not_displayed_if_not_logged_in(self):
        response = self.client.get('/')
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        self.assertFalse('Logged in as' in soup.nav.get_text())


class FilteredMovieListViewTest(TestCase):
    fixtures = ['actors.json', 'genres.json', 'movies_for_testing.json']

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

    def test_search_by_title(self):
        # Get only movies containing phrase "be"
        response = self.client.get(reverse('all_movies') + '?title__icontains=be')
        self.assertEqual(response.status_code, 200)
        found_movies = response.context['object_list']
        self.assertTrue(len(found_movies) == 3)
        self.assertEqual(
            set(found_movies.values_list('title', flat=True)),
            {'Seven Years in Tibet', 'Bell, Book and Candle', 'Pallbearer, The'}
        )

    def test_filtering_by_decades(self):
        # Assert that movies searched in each decade were in fact released in that decade
        response = self.client.get(reverse('all_movies') + f'?year_released=1919')
        found_movies = response.context['object_list']
        year_list = list(found_movies.values_list('year_released', flat=True))
        self.assertTrue(all(i <= 1919 for i in year_list))

        for year in range(1929, 2030, 10):
            response = self.client.get(reverse('all_movies') + f'?year_released={year}')
            found_movies = response.context['object_list']
            year_list = list(found_movies.values_list('year_released', flat=True))
            self.assertTrue(all(i <= year for i in year_list) and all(i >= year - 9 for i in year_list))

    def test_table_displayed_properly(self):
        response = self.client.get(reverse('all_movies') + '?title__icontains=Rocky+III')
        rocky_movie = response.context['object_list'][0]
        rocky_id = rocky_movie.id
        rocky_movielens_id = rocky_movie.movielens_id
        rocky_imdb_id = rocky_movie.imdb_id
        rocky_tmdb_id = rocky_movie.tmdb_id
        rocky_title = rocky_movie.title
        rocky_year_released = rocky_movie.year_released
        rocky_director = rocky_movie.director
        print(rocky_id, rocky_movielens_id, rocky_imdb_id, rocky_tmdb_id, rocky_title, rocky_year_released, rocky_director)
        # TODO: use BS4 to check if each field is placed in the table
        #  in the content in the correct order
        # print(response.content)

    # TODO: test sorting


class UserListViewTest(TestCase):
    fixtures = ['users_for_testing_UserListView.json']

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/all_users/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('all_users'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('all_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/user_list.html')

    def test_pagination_is_25(self):
        response = self.client.get(reverse('all_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        # Assert that the response is paginated
        self.assertTrue(response.context['is_paginated'] == True)
        # Assert that there are 25 objects on each page
        self.assertTrue(len(response.context['object_list']) == 25)

    def test_lists_all_users(self):
        # Get third page and confirm it has (exactly) remaining 22 items
        response = self.client.get(reverse('all_users') + '?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['object_list']) == 22)

    def test_search_by_title(self):
        # Get only users with usernames containing phrase "dog"
        response = self.client.get(reverse('all_users') + '?username__icontains=dog')
        self.assertEqual(response.status_code, 200)
        found_users = response.context['object_list']
        self.assertEqual(len(found_users), 2)
        self.assertEqual(
            set(found_users.values_list('username', flat=True)),
            {'ticklishdog518', 'angrydog429'}
        )


class LoginViewTest(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/login.html')


class RegisterViewTest(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/register.html')


class MovieDetailViewTest(TestCase):
    fixtures = ['genres.json', 'actors.json']

    @classmethod
    def setUpTestData(cls):
        movie_for_testing = Movie(
            movielens_id=1,
            imdb_id=114709,
            tmdb_id=862,
            title='Toy Story',
            year_released=1995,
            director='John Lasseter',
        )
        movie_for_testing.save()
        movie_for_testing.genres.add(2, 3, 4)
        movie_for_testing.actors.add(2, 3, 4)

        test_user1 = User.objects.create_user(username='testuser1', password='some_password1')
        test_user2 = User.objects.create_user(username='testuser2', password='some_password2')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/movie/1/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('movie_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('movie_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/movie_detail.html')

    def test_rating_not_visible_when_not_logged_in(self):
        response = self.client.get(reverse('movie_detail', kwargs={'pk': 1}))
        phrase_when_logged_in = 'Rate this movie'
        phrase_when_not_logged_in = 'Log in to rate'
        self.assertFalse(phrase_when_logged_in in response.content.decode('utf-8'))
        self.assertTrue(phrase_when_not_logged_in in response.content.decode('utf-8'))

    def test_logged_in_able_to_rate(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('movie_detail', kwargs={'pk': 1}))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        phrase_when_logged_in = 'Rate this movie'
        phrase_when_not_logged_in = 'Log in to rate'
        self.assertTrue(phrase_when_logged_in in response.content.decode('utf-8'))
        self.assertFalse(phrase_when_not_logged_in in response.content.decode('utf-8'))


class FilteredRatingListViewTest(TestCase):
    fixtures = ['genres.json', 'actors.json', 'movies_for_testing.json']

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='some_password1')
        test_user2 = User.objects.create_user(username='testuser_with_long_username', password='some_password2')

        all_movies = Movie.objects.all()
        no_of_movies = all_movies.count()
        movie_ids = list(all_movies.values_list('id', flat=True))
        starting_date = datetime.datetime(2018, 5, 17, 15, 34, 44, tzinfo=timezone.utc)
        for i in range(no_of_movies):
            mock_rating = Rating.objects.create(
                movie=Movie.objects.get(id=movie_ids[i]),
                who_rated=test_user1,
                value=i % 10 + 1,
                date_rated=starting_date + datetime.timedelta(days=5 * i)
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'whitepanda599'}))
        self.assertRedirects(response, '/login/?next=/profile/whitepanda599/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/rating_list_table.html')

    def test_username_displayed_if_logged_in(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        self.assertTrue('Logged in as testuser1' in soup.nav.find(id='logged-in-mobile').get_text())
        self.assertTrue('Logged in as testuser1' in soup.nav.find(id='logged-in-desktop').get_text())

    def test_username_truncated_if_too_long(self):
        login = self.client.login(username='testuser_with_long_username', password='some_password2')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser_with_long_username'}))
        self.assertEqual(str(response.context['user']), 'testuser_with_long_username')
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        self.assertTrue('Logged in as testuser_with_long_' in soup.nav.find(id='logged-in-mobile').get_text()
                        and 'username' not in soup.nav.find(id='logged-in-mobile').get_text())
        self.assertTrue('Logged in as testuser' in soup.nav.find(id='logged-in-desktop').get_text()
                        and '1' not in soup.nav.find(id='logged-in-desktop').get_text())



    # TODO: use bs4 to test if the table is displayed correctly
    # TODO: add tests to check if there is a warning saying you cannot set
    #  'date_to' earlier than 'date_from'

    def test_pagination_is_15(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        # Assert that the response is paginated
        self.assertTrue(response.context['is_paginated'] == True)
        # Assert that there are 15 objects on each page
        self.assertTrue(len(response.context['object_list']) == 15)

    def test_lists_all_ratings(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}) + '?page=4')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['object_list']) == 5)

    def test_filtering_by_decades(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}) +
                                   f'?movie__year_released=1919'
                                   + '&date_from=&date_to=')
        found_ratings = response.context['object_list']
        year_list = list(found_ratings.values_list('movie__year_released', flat=True))
        self.assertTrue(all(i <= 1919 for i in year_list))

        for year in range(1929, 2030, 10):
            response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}) +
                                       f'?movie__year_released={year}'
                                       + '&date_from=&date_to=')
            found_ratings = response.context['object_list']
            year_list = list(found_ratings.values_list('movie__year_released', flat=True))
            self.assertTrue(all(i <= year for i in year_list) and all(i >= year - 9 for i in year_list))

    def test_filtering_by_ratings(self):
        login = self.client.login(username='testuser1', password='some_password1')
        for value in range(1, 11):
            response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}) +
                                       f'?value={value}'
                                       + '&date_from=&date_to=')
            found_ratings = response.context['object_list']
            rating_list = list(found_ratings.values_list('value', flat=True))
            self.assertTrue(all(i <= value for i in rating_list) and all(i >= value - 9 for i in rating_list))

    def test_filtering_by_date(self):
        login = self.client.login(username='testuser1', password='some_password1')
        date_from = datetime.datetime(2018, 9, 27, 10, 10, 10, tzinfo=timezone.utc)
        date_to = datetime.datetime(2019, 1, 3, 10, 10, 10, tzinfo=timezone.utc)
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}) +
                                   f"?date_from={date_from.strftime('%Y-%m-%d')}&date_to={date_to.strftime('%Y-%m-%d')}")
        found_ratings = response.context['object_list']
        date_list = list(found_ratings.values_list('date_rated', flat=True))
        self.assertTrue(all(i <= date_to for i in date_list) and all(i >= date_from for i in date_list))

    def test_rating_belong_to_the_user(self):
        test_user = User.objects.first()
        login = self.client.login(username=test_user.username, password='some_password1')
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser1'}))
        ratings = response.context['object_list']
        ratings_owners = list(ratings.values_list('who_rated', flat=True))
        self.assertTrue(all(i == test_user.id for i in ratings_owners))


class UserStatsViewTest(TestCase):
    fixtures = ['genres.json', 'actors.json', 'movies_for_testing.json']

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='some_password1')

        all_movies = Movie.objects.all()
        no_of_movies = all_movies.count()
        movie_ids = list(all_movies.values_list('id', flat=True))
        starting_date = datetime.datetime(2018, 5, 17, 15, 34, 44, tzinfo=timezone.utc)
        for i in range(no_of_movies):
            mock_rating = Rating.objects.create(
                movie=Movie.objects.get(id=movie_ids[i]),
                who_rated=test_user1,
                value=i % 10 + 1,
                date_rated=starting_date + datetime.timedelta(days=5 * i)
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('user_stats', kwargs={'username': 'testuser1'}))
        self.assertRedirects(response, '/login/?next=/profile/testuser1/stats/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='some_password1')
        response = self.client.get(reverse('user_stats', kwargs={'username': 'testuser1'}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/stats.html')

    # TODO: use bs4 to check if frontend is displayed correctly
    #
    # def test_frontend(self):
    #     response = self.client.get(reverse('all_movies'))
    #     soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
    #     # print(soup.prettify())
    #     print(soup.table)


class RecommendViewTest(TestCase):
    pass


class EstablishPreferencesViewTest(TestCase):
    pass


class PasswordResetViewTest(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/password-reset/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/password_reset.html')


class PasswordResetDoneViewTest(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/password-reset/done/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/password_reset_done.html')

# Old tests

# class MovieGroupingTestCase(TestCase):
#     fixtures = fixtures
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
