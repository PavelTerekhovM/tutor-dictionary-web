import json
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
        self.assertEqual(2, len(Lesson.objects.all()))
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


class BaseLearnView(BaseTestSettings):
    """
    Base class for testing LearnView requests
    """
    fixtures = [
        'users.json',
        'words.json',
        'dictionaries.json',
        'lessons.json',
        'cards.json'
    ]


class TestLearnViewGet(BaseLearnView):
    """
    Testcase for testing LearnView GET request
    """

    def test_get_not_student(self):
        """
        Testing GET by users who aren't students
        """
        lesson = Lesson.objects.latest('created')

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        url_redirect = reverse('dictionary:my_dictionaries')

        # testting access to lesson with private dict by unauth user
        res = self.client.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # testting access to lesson with private dict by auth user
        res = self.client_auth.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # change status public and check
        self.assertEqual(
            'private',
            lesson.dictionary.status
        )
        lesson.dictionary.status = 'public'
        lesson.save()
        self.assertEqual(
            'public',
            lesson.dictionary.status,
        )

        # testting access to lesson with public dict by unauth user
        res = self.client.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # testting access to lesson with public dict by auth user
        res = self.client_auth.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_get_by_student(self):
        """
        Testing get request from student of lesson
        """
        # add auth user to student lists
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        res = self.client_auth.get(url)

        # check status code 200 and card, next_card and form in context
        self.assertEqual(200, res.status_code)
        self.assertIn('next_card', res.context_data)
        self.assertIn('form', res.context_data)
        self.assertIn('card', res.context_data)
        self.assertIn('reverse', res.context_data)
        self.assertIsNone(res.context_data.get('reverse'))

        # check form is unbound, contain 'body', card_pk, translation
        self.assertFalse(res.context_data.get('form').is_bound)
        self.assertIn('card_pk', res.context_data.get('form').fields)
        self.assertIn('body', res.context_data.get('form').fields)
        self.assertIn('translations', res.context_data.get('form').fields)

        # check card is among cards of lesson and next_card exists
        self.assertIn(
            res.context_data.get('card').word,
            lesson.dictionary.word.all()
        )
        self.assertTrue(res.context_data.get('next_card'))

        # check if reverse translation works
        url = reverse(
            'lesson:learn',
            kwargs={
                'lesson_pk': lesson.pk,
                'reverse': 'reverse'
            }
        )
        res = self.client_auth.get(url)

        self.assertIn('reverse', res.context_data)
        self.assertEqual('reverse', res.context_data.get('reverse'))

    def test_get_no_active_cards(self):
        """
        Testing get request from student to lesson with one or no active cards
        """
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)

        # set all cards as 'done'
        for card in lesson.card_set.all():
            card.status = 'done'
            card.save()

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        url_redirect = reverse(
            'lesson:lesson',
            kwargs={
                'dictionary_pk': lesson.dictionary.pk,
                'user_pk': self.user_auth.pk,
            }
        )

        # check 302 status if no cards available
        res = self.client_auth.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # set one cards as 'active'
        card = lesson.card_set.latest('created')
        card.status = 'active'
        card.save()

        # check 200 status and next_card is False
        res = self.client_auth.get(url)
        self.assertEqual(200, res.status_code)
        self.assertIn('next_card', res.context_data)
        self.assertIn('form', res.context_data)
        self.assertIn('card', res.context_data)
        self.assertFalse(res.context_data.get('next_card'))

        # set one cards as 'disable'
        card = lesson.card_set.latest('created')
        card.status = 'disable'
        card.save()

        # check 302 status if no cards available
        res = self.client_auth.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)


class TestLearnViewGetAJAX(BaseLearnView):
    """
    Testcase for testing LearnView AJAX GET request
    """

    def test_get_by_student_ajax(self):
        """
        Testing AJAX GET requests by users who is student
        """
        # add auth user to student lists
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        header = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        res = self.client_auth.get(url, **header)

        # check status code 200 and 'application/json' as Content-Type
        self.assertEqual(200, res.status_code)
        self.assertIn('application/json', res.headers.get('Content-Type'))

        # check if next_card, msg, status, card, reverse in content
        self.assertIn('msg', json.loads(res.content))
        self.assertIn('status', json.loads(res.content))
        self.assertIn('next_card', json.loads(res.content))
        self.assertIn('card', json.loads(res.content))
        self.assertIn('card_pk', json.loads(res.content))
        self.assertIn('reverse', json.loads(res.content))

        # check card is among cards of lesson and next_card exists
        self.assertIn(
            json.loads(res.content).get('card_pk'),
            lesson.dictionary.word.all().values_list(flat=True)
        )
        self.assertTrue(json.loads(res.content).get('next_card'))

        # check if reverse translation works
        url = reverse(
            'lesson:learn',
            kwargs={
                'lesson_pk': lesson.pk,
                'reverse': 'reverse'
            }
        )
        res = self.client_auth.get(url, **header)

        self.assertIn('reverse', json.loads(res.content))
        self.assertEqual('reverse', json.loads(res.content).get('reverse'))

    def test_get_no_active_cards_ajax(self):
        """
        Testing AJAX GET request from student to lesson with one/no active card
        """
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)

        # set all cards as 'done'
        for card in lesson.card_set.all():
            card.status = 'done'
            card.save()

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        url_redirect = reverse(
            'lesson:lesson',
            kwargs={
                'dictionary_pk': lesson.dictionary.pk,
                'user_pk': self.user_auth.pk,
            }
        )
        header = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # check 200 status if no cards available
        res = self.client_auth.get(url, **header)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.headers.get('Content-Type'))
        self.assertIn('msg', json.loads(res.content))
        self.assertIn('status', json.loads(res.content))
        self.assertEqual('danger', json.loads(res.content).get('status'))
        self.assertEqual(
            'В выбранном словаре нет активных карточек, '
            'измените настройки словаря и попробуйте снова.',
            json.loads(res.content).get('msg')
        )

        # set one cards as 'active'
        card = lesson.card_set.latest('created')
        card.status = 'active'
        card.save()

        # check 200 status and next_card is False
        res = self.client_auth.get(url, **header)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.headers.get('Content-Type'))
        self.assertIn('card', json.loads(res.content))
        self.assertIn('card_pk', json.loads(res.content))
        self.assertIn('next_card', json.loads(res.content))
        self.assertFalse(json.loads(res.content).get('next_card'))

        # set one cards as 'disable'
        card = lesson.card_set.latest('created')
        card.status = 'disable'
        card.save()

        res = self.client_auth.get(url, **header)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.headers.get('Content-Type'))
        self.assertEqual('danger', json.loads(res.content).get('status'))


class TestLearnViewPost(BaseLearnView):
    """
    Testcase for testing LearnView POST request
    """

    def test_post_not_student(self):
        """
        Testing POST by users who aren't students
        """
        lesson = Lesson.objects.latest('created')
        card = lesson.card_set.latest('created')

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        url_redirect = reverse('dictionary:my_dictionaries')

        payload = {
            'card_pk': card.pk,
            'body': card.word.body,
            'translations': '',
        }

        # testing POST requests to lesson with private dict by unauth user
        res = self.client.post(url, payload)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # testing access to lesson with private dict by auth user
        res = self.client_auth.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # change status public and check
        self.assertEqual(
            'private',
            lesson.dictionary.status
        )
        lesson.dictionary.status = 'public'
        lesson.save()
        self.assertEqual(
            'public',
            lesson.dictionary.status,
        )

        # testing POST request to lesson with public dict by unauth user
        res = self.client.post(url, payload)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # testing POST request to lesson with public dict by auth user
        res = self.client_auth.get(url)
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_post_by_student(self):
        """
        Testing POST request from student of lesson
        """
        # add auth user to student lists
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)
        card = lesson.card_set.latest('created')
        correct_answers = card.correct_answers

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )

        payload = {
            'card_pk': card.pk,
            'body': card.word.body,
            'translations': '',
        }
        res = self.client_auth.post(url, payload)

        # check status code 200 and card, next_card and form in context
        self.assertEqual(200, res.status_code)
        self.assertIn('form', res.context_data)
        self.assertIn('card', res.context_data)
        self.assertIn('reverse', res.context_data)

        # check message confirm correct answer, form is_bound and valid
        self.assertIn(
            'Это верный ответ',
            list(res.context['messages'])[0].message
        )
        self.assertEqual('success', list(res.context['messages'])[0].tags)
        self.assertTrue(res.context_data.get('form').is_bound)
        self.assertTrue(res.context_data.get('form').is_valid())

        # check if number of correct answers incremented
        card.refresh_from_db()
        self.assertEqual(correct_answers + 1, card.correct_answers)

        # check if reverse translation works
        correct_answers = card.correct_answers
        url = reverse(
            'lesson:learn',
            kwargs={
                'lesson_pk': lesson.pk,
                'reverse': 'reverse'
            }
        )
        payload = {
            'card_pk': card.pk,
            'body': '',
            'translations': card.word.translations,
        }

        res = self.client_auth.post(url, payload)

        # check status code 200 and reverse in context
        self.assertEqual(200, res.status_code)
        self.assertIn('reverse', res.context_data)
        self.assertEqual('reverse', res.context_data.get('reverse'))

        #  check message confirms correct answer
        self.assertIn(
            'Это верный ответ',
            list(res.context['messages'])[0].message
        )
        self.assertEqual('success', list(res.context['messages'])[0].tags)

        # check if number of correct answers incremented
        card.refresh_from_db()
        self.assertEqual(correct_answers + 1, card.correct_answers)

    def test_post_by_student_negative(self):
        """
        Testing POST request from student of lesson with wrong answer
        """
        # add auth user to student lists
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)
        card = lesson.card_set.latest('created')
        correct_answers = card.correct_answers

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )

        payload = {
            'card_pk': card.pk,
            'body': 'wrong_answer',
            'translations': '',
        }
        res = self.client_auth.post(url, payload)

        # check status code 200 and card, next_card and form in context
        self.assertEqual(200, res.status_code)
        self.assertIn('form', res.context_data)
        self.assertIn('card', res.context_data)
        self.assertIn('reverse', res.context_data)

        # check message confirm incorrect answer, form is_bound and valid
        self.assertIn(
            'Это неверный ответ',
            list(res.context['messages'])[0].message
        )
        self.assertEqual('warning', list(res.context['messages'])[0].tags)
        self.assertTrue(res.context_data.get('form').is_bound)
        self.assertTrue(res.context_data.get('form').is_valid())

        # check if number of correct answers unchanged
        card.refresh_from_db()
        self.assertEqual(correct_answers, card.correct_answers)

        # check if reverse translation works
        correct_answers = card.correct_answers
        url = reverse(
            'lesson:learn',
            kwargs={
                'lesson_pk': lesson.pk,
                'reverse': 'reverse'
            }
        )
        payload = {
            'card_pk': card.pk,
            'body': '',
            'translations': 'wrong_answer',
        }

        res = self.client_auth.post(url, payload)

        # check status code 200 and reverse in context
        self.assertEqual(200, res.status_code)
        self.assertIn('reverse', res.context_data)
        self.assertEqual('reverse', res.context_data.get('reverse'))

        #  check message confirms incorrect answer
        self.assertIn(
            'Это неверный ответ',
            list(res.context['messages'])[0].message
        )
        self.assertEqual('warning', list(res.context['messages'])[0].tags)

        # check if number of correct answers incremented
        card.refresh_from_db()
        self.assertEqual(correct_answers, card.correct_answers)


class TestLearnViewPostAJAX(BaseLearnView):
    """
    Testcase for testing LearnView AJAX POST request
    """

    def test_post_by_student_ajax(self):
        """
        Testing AJAX POST requests by users who is student
        """
        # add auth user to student lists
        lesson = Lesson.objects.get(pk=1)
        lesson.dictionary.student.add(self.user_auth)

        card = lesson.card_set.latest('created')
        correct_answers = card.correct_answers

        url = reverse(
            'lesson:learn',
            kwargs={'lesson_pk': lesson.pk}
        )
        header = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        payload = {
            'card_pk': card.pk,
            'body': card.word.body,
            'translations': '',
        }
        res = self.client_auth.post(url, **header, data=payload)

        # check status code 200 and 'application/json' as Content-Type
        self.assertEqual(200, res.status_code)
        self.assertIn('application/json', res.headers.get('Content-Type'))

        # check if next_card, msg, status, card, reverse in content
        self.assertIn('msg', json.loads(res.content))
        self.assertIn('status', json.loads(res.content))
        self.assertIn('next_card', json.loads(res.content))
        self.assertIn('card', json.loads(res.content))
        self.assertIn('card_pk', json.loads(res.content))
        self.assertIn('reverse', json.loads(res.content))

        #  check message confirms correct answer
        self.assertIn('Это верный ответ', json.loads(res.content).get('msg'))
        self.assertEqual('success', json.loads(res.content).get('status'))

        # check if number of correct answers incremented
        card.refresh_from_db()
        self.assertEqual(correct_answers + 1, card.correct_answers)

        # check if reverse translation works
        correct_answers = card.correct_answers
        url = reverse(
            'lesson:learn',
            kwargs={
                'lesson_pk': lesson.pk,
                'reverse': 'reverse'
            }
        )
        payload = {
            'card_pk': card.pk,
            'body': '',
            'translations': card.word.translations,
        }
        res = self.client_auth.post(url, **header, data=payload)

        # check status code 200 and 'application/json' as Content-Type
        self.assertEqual(200, res.status_code)
        self.assertIn('application/json', res.headers.get('Content-Type'))

        #  check message confirms correct answer
        self.assertIn('Это верный ответ', json.loads(res.content).get('msg'))
        self.assertEqual('success', json.loads(res.content).get('status'))

        # check if number of correct answers incremented
        card.refresh_from_db()
        self.assertEqual(correct_answers + 1, card.correct_answers)
