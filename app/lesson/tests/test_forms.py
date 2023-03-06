import os

from django.conf import settings

from django.test import Client

from django.contrib.auth.models import User
from django.urls import reverse

from dictionary.models import Dictionary, Word
from dictionary.tests.test_views import BaseTestSettings
from lesson.models import Lesson, Card


class TestChangeNumberAnswersForm(BaseTestSettings):
    """
    Testcase for testing form of changing number of required answers
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

    def test_rendering_form(self):
        """
        Testing lesson view include form
        """
        tested_lesson = Lesson.objects.create(
            dictionary_id=Dictionary.objects.latest('created').pk,
            student_id=self.user_auth.pk
        )
        url = reverse(
            'lesson:lesson',
            kwargs={
                'user_pk': self.user_auth.pk,
                'dictionary_pk': tested_lesson.dictionary.pk
            }
        )

        res = self.client_auth.get(url)
        self.assertEqual(200, res.status_code)
        self.assertIn('form_answers', res.context)
        self.assertFalse(res.context.get('form_answers').is_bound)
        self.assertEqual(2, len(res.context.get('form_answers').fields))
        self.assertIn(
            'required_answers',
            res.context.get('form_answers').fields
        )
        self.assertIn('lesson_pk', res.context.get('form_answers').fields)

    def test_sending_invalid_form(self):
        """
        Testing POST request with invalid data
        """
        tested_lesson = Lesson.objects.create(
            dictionary_id=Dictionary.objects.latest('created').pk,
            student_id=self.user_auth.pk
        )
        url = reverse(
            'lesson:change_number_answers'
        )

        res = self.client_auth.post(
            url,
            {
                'lesson_pk': tested_lesson.pk
            }
        )
        self.assertEqual(404, res.status_code)

        res = self.client_auth.post(
            url,
            {
                'required_answers': 2,
            }
        )
        self.assertEqual(404, res.status_code)


class TestChangeCardStatus(BaseTestSettings):
    """
    Testcase for testing form of changing status of card
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

    def test_rendering_form(self):
        """
        Testing lesson view include forms
        """
        tested_lesson = Lesson.objects.create(
            dictionary_id=Dictionary.objects.latest('created').pk,
            student_id=self.user_auth.pk
        )
        url = reverse(
            'lesson:lesson',
            kwargs={
                'user_pk': self.user_auth.pk,
                'dictionary_pk': tested_lesson.dictionary.pk
            }
        )

        tested_card = Card.objects.create(
            word=Word.objects.latest('created'),
            lesson=tested_lesson
        )

        res = self.client_auth.get(url)
        self.assertEqual(200, res.status_code)
        self.assertIn('action="/change_card_status/', res.content.decode())
