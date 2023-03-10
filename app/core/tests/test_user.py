from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from dictionary.tests.test_views import BaseTestSettings


class TestView(BaseTestSettings):
    """
    Testcase for core.User
    """
    def test_SignUpView(self):
        """
        Testing SignUpView view
        """
        url = reverse(
            'register'
        )

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertEqual('registration/register.html', res.template_name[0])
        self.assertEqual(
            'UserRegistrationForm',
            res.context_data.get('form').__class__.__name__
        )

    def test_PasswordChangeView(self):
        """
        Testing PasswordChangeView view
        """
        url = reverse(
            'password_change'
        )

        res = self.client_auth.get(url)

        self.assertEqual(200, res.status_code)
        self.assertEqual(
            'registration/password_change_form.html',
            res.template_name[0]
        )
        self.assertEqual(
            'MyPasswordChangeForm',
            res.context_data.get('form').__class__.__name__
        )


class TestForm(BaseTestSettings):
    """
    Testcase for core.User
    """
    def test_UserRegistrationForm(self):
        """
        Testing UserRegistrationForm
        """
        url = reverse(
            'register'
        )

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertFalse(
            res.context_data.get('form').is_bound
        )
        # email same as self.user_auth has
        invalid_email = {
            'username': 'test_user',
            'email': 'user_2@example.com',
            'password1': '123test52T',
            'password2': '123test52T',
        }

        res = self.client.post(
            url,
            invalid_email
        )
        self.assertEqual(200, res.status_code)
        self.assertTrue(
            res.context_data.get('form').is_bound
        )
        self.assertFalse(
            res.context_data.get('form').is_valid()
        )
        self.assertEqual(
            'Пользователь с такой почтой уже зарегистрирован',
            res.context_data.get('form').errors.get('__all__')[0]
        )

        # success registration
        valid_email = {
            'username': 'test_user',
            'email': 'user@example.com',
            'password1': '123test52T',
            'password2': '123test52T',
        }

        self.assertEqual(2, len(get_user_model().objects.all()))
        res = self.client.post(
            url,
            valid_email
        )
        self.assertEqual(302, res.status_code)
        self.assertEqual(3, len(get_user_model().objects.all()))
        self.assertTrue(
            get_user_model().objects.filter(username='test_user').exists()
        )
