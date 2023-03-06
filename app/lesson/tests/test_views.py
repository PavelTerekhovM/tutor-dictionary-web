import os

from django.conf import settings

from django.test import Client

from django.contrib.auth.models import User
from django.urls import reverse

from dictionary.models import Dictionary
from dictionary.tests.test_views import BaseTestSettings
from lesson.models import Lesson


class TestChangeNumberAnswers(BaseTestSettings):
    """
    Testcase for testing views of changing number of required answers
    """
    def setUp(self):
        user = {
            'username': 'test_user_1',
            'email': 'user_1@example.com',
            'password': 'testpass123',
        }
        self.user = User.objects.create_user(**user)

        user_authenticated = {
            'username': 'test_user_2',
            'email': 'user_2@example.com',
            'password': 'testpass456',
        }
        self.user_auth = User.objects.create_user(**user_authenticated)
        self.client_auth = Client()
        self.client_auth.force_login(self.user_auth)

        sample_file = os.path.join(
            settings.BASE_DIR,
            'lesson/tests/sample_file/valid_dict_file.xml'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                reverse('upload_file'),
                {
                    'author': self.user_auth.pk,
                    'note': 'test file',
                    'status': 'public',
                    'file': fp
                }
            )

    def test_get_unauthenticated(self):
        """
        Testing GET request with unauthenticated user
        """
        url = reverse(
            'lesson:change_number_answers'
        )
        url_redirect = '/login/?next=/change_number_answers/'

        res = self.client.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_post_unauthenticated(self):
        """
        Testing POST request with unauthenticated user
        """
        url = reverse(
            'lesson:change_number_answers'
        )
        url_redirect = '/login/?next=/change_number_answers/'

        res = self.client.post(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_get_authenticated(self):
        """
        Testing GET request with authenticated user
        """
        url = reverse(
            'lesson:change_number_answers'
        )

        res = self.client_auth.get(url)
        self.assertEqual(404, res.status_code)
        self.assertEqual('<h1>Page not found</h1>', res.content.decode())

    def test_post_authenticated(self):
        """
        Testing POST request with authenticated user
        """
        url = reverse(
            'lesson:change_number_answers'
        )
        Lesson.objects.create(
            dictionary_id=Dictionary.objects.latest('created').pk,
            student_id=self.user_auth.pk
        )

        # check if there is one lesson and number answers is 5
        tested_lesson = Lesson.objects.latest('created')
        self.assertEqual(1, len(Lesson.objects.all()))
        self.assertEqual(5, tested_lesson.required_answers)

        res = self.client_auth.post(
            url,
            {
                'required_answers': 2,
                'lesson_pk': tested_lesson.pk
            }
        )

        returned_url = reverse(
            'lesson:lesson',
            kwargs={
                'user_pk': self.user_auth.pk,
                'dictionary_pk': tested_lesson.dictionary.pk
            }
        )

        self.assertEqual(302, res.status_code)
        self.assertEqual(returned_url, res.url)

        # check if there is still one lesson and number answers changed to 2
        tested_lesson.refresh_from_db()
        self.assertEqual(1, len(Lesson.objects.all()))
        self.assertEqual(2, tested_lesson.required_answers)
