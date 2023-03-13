import os

from django.conf import settings
from django.urls import reverse

from dictionary.models import Dictionary, Word
from dictionary.tests.test_views import BaseTestSettings
from lesson.models import Lesson, Card


class TestChangeNumberAnswers(BaseTestSettings):
    """
    Testcase for testing views of changing number of required answers
    """
    def setUp(self):
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file.xml'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                reverse('dictionary:upload_file'),
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
        url_redirect = reverse('login') + '?next=' + url

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
        url_redirect = reverse('login') + '?next=' + url

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
        # as GET not allowed should return 405
        self.assertEqual(405, res.status_code)

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

        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.headers.get('Content-Type'))
        self.assertIn('action_status', res.content.decode())

        # check if there is still one lesson and number answers changed to 2
        tested_lesson.refresh_from_db()
        self.assertEqual(1, len(Lesson.objects.all()))
        self.assertEqual(2, tested_lesson.required_answers)


class TestChangeCardStatus(BaseTestSettings):
    """
    Testcase for testing views of changing card status
    """
    def setUp(self):
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file.xml'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                reverse('dictionary:upload_file'),
                {
                    'author': self.user_auth.pk,
                    'note': 'test file',
                    'status': 'public',
                    'file': fp
                }
            )

    def test_get_unauthenticated(self):
        """
        Testing GET request to change card status by  unauthenticated user
        """
        url = reverse(
            'lesson:change_card_status'
        )
        url_redirect = reverse('login') + '?next=' + url

        res = self.client.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_post_unauthenticated(self):
        """
        Testing POST request to change card status by unauthenticated user
        """
        url = reverse(
            'lesson:change_card_status'
        )
        url_redirect = reverse('login') + '?next=' + url

        res = self.client.post(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_get_authenticated(self):
        """
        Testing GET request to change card status by authenticated user
        """
        url = reverse(
            'lesson:change_card_status'
        )

        res = self.client_auth.get(url)
        self.assertEqual(405, res.status_code)

    def test_post_authenticated(self):
        """
        Testing POST request to change card status by authenticated user
        """
        url = reverse(
            'lesson:change_card_status'
        )
        Lesson.objects.create(
            dictionary_id=Dictionary.objects.latest('created').pk,
            student_id=self.user_auth.pk
        )

        # check if there is one lesson and number answers is 5
        tested_lesson = Lesson.objects.latest('created')
        self.assertEqual(0, len(tested_lesson.card_set.all()))

        tested_card = Card.objects.create(
            word=Word.objects.latest('created'),
            lesson=tested_lesson
        )
        Lesson.objects.create(
            dictionary=Dictionary.objects.latest('created'),
            student=self.user_auth
        )
        # check default status of card 'active' and 0 correct answers
        self.assertEqual('active', tested_card.status)
        self.assertEqual(0, tested_card.correct_answers)

        res = self.client_auth.post(
            url,
            {
                'status': 'done',
                'card_pk': tested_card.pk,
                'back_url': '/',
            }
        )

        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.url)

        # check if status of card changed to done and 5 correct answers
        tested_card.refresh_from_db()
        self.assertEqual('done', tested_card.status)
        self.assertEqual(5, tested_card.correct_answers)

        res = self.client_auth.post(
            url,
            {
                'status': 'active',
                'card_pk': tested_card.pk,
                'back_url': '/',
            }
        )

        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.url)

        # check if status of card changed to done and 5 correct answers
        tested_card.refresh_from_db()
        self.assertEqual('active', tested_card.status)
        self.assertEqual(0, tested_card.correct_answers)
