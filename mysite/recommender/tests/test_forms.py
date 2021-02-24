from django.test import TestCase, SimpleTestCase

from recommender.forms import UserRegisterForm, UserRatingForm


class UserRegisterFormTest(SimpleTestCase):
    def test_correct_fields_are_used(self):
        form = UserRegisterForm()
        self.assertEqual(
            set(form.fields.keys()),
            {'username', 'email', 'password1', 'password2'}
        )


class UserRatingFormTest(SimpleTestCase):
    def test_correct_fields_are_used(self):
        form = UserRatingForm()
        self.assertEqual(
            set(form.fields.keys()),
            {'value'}
        )

    def test_label_is_empty(self):
        form = UserRatingForm()
        print(form.fields['value'].label)
        self.assertEqual(form.fields['value'].label, '')

    def test_correct_value_lower_limit(self):
        form = UserRatingForm(data={'value': 1})
        self.assertTrue(form.is_valid())

    def test_correct_value_upper_limit(self):
        form = UserRatingForm(data={'value': 10})
        self.assertTrue(form.is_valid())

    def test_correct_value_middle(self):
        form = UserRatingForm(data={'value': 5})
        self.assertTrue(form.is_valid())

    def test_value_smaller_than_lower_limit(self):
        form = UserRatingForm(data={'value': -1})
        self.assertFalse(form.is_valid())

    def test_value_greater_than_upper_limit(self):
        form = UserRatingForm(data={'value': 11})
        self.assertFalse(form.is_valid())

