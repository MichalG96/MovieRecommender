from django.test import TestCase


class BasicUrlsTestCase(TestCase):

    def test_homepage_response_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommender/homepage.html')

    def test_all_movies_response_status_code(self):
        response = self.client.get('/all_movies/')
        self.assertEqual(response.status_code, 200)

    def test_all_users_response_status_code(self):
        response = self.client.get('/all_users/')
        self.assertEqual(response.status_code, 200)

    def test_login_response_status_code(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_register_response_status_code(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    # # TODO: consider logged in and logged out users
    # def test_profile_response_status_code(self):
    #     response = self.client.get('/profile/')
    #     print(response)
    #     self.assertEqual(response.status_code, 200)
