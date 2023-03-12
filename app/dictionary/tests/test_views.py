import os

from django.conf import settings
from django.contrib.auth import get_user_model

from django.urls import reverse
from django.test import Client

from core.tests.base_settings import BaseTestSettings
from dictionary.models import Dictionary, Word


class AddDictionaryView(BaseTestSettings):
    """
    Testcase for testing views of dictionary-app
    """

    def test_AddDictionaryView_unauth(self):
        """
        Testing redirect when unauthenticated try to access /upload URL
        """
        url = reverse(
            'dictionary:upload_file'
        )
        url_redirect = reverse('login') + '?next=' + url

        res = self.client.get(url)

        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    def test_AddDictionaryView_auth(self):
        """
        Testing creating dictionary by authenticated user on /upload URL
        """
        url = reverse(
            'dictionary:upload_file'
        )
        url_redirect = reverse('dictionary:my_dictionaries')

        # testing GET request: status code 200,
        # form with file field is available
        res = self.client_auth.get(url)
        self.assertEqual(200, res.status_code)
        self.assertTrue(res.context.get('user').is_authenticated)
        self.assertIn(
            'file',
            res.context.get('form').fields.keys()
        )

        # testing POST request: status code 302,
        # provided file saved in db
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file.xml'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                url,
                {
                    'author': self.user_auth.pk,
                    'note': 'test file',
                    'status': 'public',
                    'file': fp
                }
            )

        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)
        self.assertEqual(1, len(Dictionary.objects.all()))
        self.assertEqual(
            'test file',
            Dictionary.objects.latest('created').note
        )
        self.assertEqual(
            'Test 2022.07.13',
            Dictionary.objects.latest('created').title,
        )
        self.assertEqual(
            25,
            Dictionary.objects.latest('created').word.count(),
        )
        self.assertEqual(
            'test-2022-07-13',
            Dictionary.objects.latest('created').slug,
        )

    def test_AddDictionaryView_auth_invalid_files(self):
        """
        Testing creating dictionary by authenticated user with invalid files
        """
        url = reverse(
            'dictionary:upload_file'
        )
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/dict_file_with_invalid_structure.xml'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                url,
                {
                    'author': self.user_auth.pk,
                    'note': 'test file',
                    'status': 'public',
                    'file': fp
                }
            )

        self.assertEqual(200, res.status_code)
        self.assertTrue(res.context.get('form').is_bound)
        self.assertFalse(res.context.get('form').is_valid())
        self.assertEqual(
            'Загруженный файл не был распознан',
            res.context.get('form').errors.get('file')[0]
        )

    def test_AddDictionaryView_auth_csv_files(self):
        """
        Testing creating dictionary by authenticated user with csv files
        """
        url = reverse(
            'dictionary:upload_file'
        )
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/csv_file.csv'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                url,
                {
                    'author': self.user_auth.pk,
                    'note': 'test file',
                    'status': 'public',
                    'file': fp
                }
            )

        self.assertEqual(200, res.status_code)
        self.assertTrue(res.context.get('form').is_bound)
        self.assertFalse(res.context.get('form').is_valid())
        self.assertEqual(
            'Загруженный файл не был распознан',
            res.context.get('form').errors.get('file')[0]
        )


class Dictionary_detail(BaseTestSettings):
    """
    Testcase for testing rendering Dictionary_detail view
    """

    def setUp(self):
        new_word = {'body': 'test_word', 'translations': 'слово'}
        self.new_word = Word.objects.create(**new_word)

        new_dict = {
            'title': 'test_dict',
            'status': 'public',
            'author': self.user_auth
        }
        self.new_dict = Dictionary.objects.create(**new_dict)
        self.new_dict.word.add(self.new_word)

    def test_Dictionary_detail_unauth(self):
        """
        Testing rendering dictionaries for unauthenticated users
        """
        url = reverse(
            'dictionary:dictionary_detail',
            kwargs={'pk': Dictionary.objects.latest('created').pk}
        )
        self.assertEqual(1, len(Dictionary.objects.all()))
        self.assertEqual(1, len(Word.objects.all()))

        res = self.client.get(url)
        self.assertEqual(200, res.status_code)
        self.assertEqual(
            'dictionary/detail.html',
            res.template_name[0]
        )
        self.assertEqual(
            'dictionary/detail.html',
            res.template_name[0]
        )
        self.assertEqual(
            'ChoiceDictionaryForm',
            res.context_data.get('form').__class__.__name__
        )

    def test_Dictionary_detail_auth(self):
        """
        Testing rendering dictionaries for authenticated users
        """
        url = reverse(
            'dictionary:dictionary_detail',
            kwargs={'pk': Dictionary.objects.latest('created').pk}
        )
        self.assertEqual(1, len(Dictionary.objects.all()))
        self.assertEqual(1, len(Word.objects.all()))

        res = self.client_auth.get(url)
        self.assertEqual(200, res.status_code)
        self.assertEqual(
            'dictionary/detail.html',
            res.template_name[0]
        )
        self.assertEqual(
            'dictionary/detail.html',
            res.template_name[0]
        )
        self.assertEqual(
            'ChoiceDictionaryForm',
            res.context_data.get('form').__class__.__name__
        )


class AddRemoveDictionary(BaseTestSettings):
    """
    Testcase for testing add_dictionary and remove views
    """

    def setUp(self):

        self.create_dictionary()

        new_auth_user = {
            'username': 'test_user_3',
            'email': 'user_3@example.com',
            'password': 'testpass123',
        }
        self.new_auth_user = get_user_model().objects.create_user(
            **new_auth_user
        )
        self.client_new_auth_user = Client()
        self.client_new_auth_user.force_login(self.new_auth_user)

    def test_add_dictionary(self):
        """
        Testing add view to test:
        - create a dictionary with self.user_auth author
        - create a second auth user
        - send a POST request to add new user to this dictionary
        """
        url = reverse(
            'dictionary:add_dictionary'
        )
        url_redirect = reverse('login') + '?next=' + url

        self.assertEqual(
            0, len(Dictionary.objects.latest('created').student.all())
        )
        # test that only POST and authorised users allowed
        self.assertEqual(405, self.client_auth.get(url).status_code)
        self.assertEqual(302, self.client.get(url).status_code)
        self.assertEqual(url_redirect, self.client.get(url).url)

        payload = {
            'dictionary_pk': Dictionary.objects.latest('created').pk
        }
        url_redirect = reverse(
            'lesson:lesson',
            kwargs={
                'user_pk': self.new_auth_user.pk,
                'dictionary_pk': Dictionary.objects.latest('created').pk,
            }
        )

        res = self.client_new_auth_user.post(
            url,
            payload,
        )
        # test that POST was successfully handled
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # test that that number of students changed
        self.assertEqual(
            1, len(Dictionary.objects.latest('created').student.all())
        )

    def test_remove_dictionary(self):
        """
        Testing remove view to test:
        - create a dictionary with self.user_auth author in (setUp)
        - create a second auth user
        - add second user to students
        - send a POST request to add new user to this dictionary
        """
        url = reverse(
            'dictionary:remove_dictionary'
        )
        url_redirect = reverse('login') + '?next=' + url

        self.new_dict.student.add(self.new_auth_user)
        self.assertEqual(
            1, len(Dictionary.objects.latest('created').student.all())
        )
        # test that only POST and authorised users allowed
        self.assertEqual(405, self.client_auth.get(url).status_code)
        self.assertEqual(302, self.client.get(url).status_code)
        self.assertEqual(url_redirect, self.client.get(url).url)

        payload = {
            'dictionary_pk': Dictionary.objects.latest('created').pk
        }

        url_redirect = reverse(
            'dictionary:dictionary_detail',
            kwargs={
                'pk': Dictionary.objects.latest('created').pk,
            }
        )
        res = self.client_new_auth_user.post(
            url,
            payload,
        )
        # test that POST was successfully handled
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # test that that number of students changed
        self.assertEqual(
            0, len(Dictionary.objects.latest('created').student.all())
        )


class ChangeStatus(BaseTestSettings):
    """
    Testcase for testing change_status views
    """

    def setUp(self):
        self.create_dictionary()

    def test_negative(self):
        """
        Testing negative scenarios of changing status:
        - create a dictionary with self.user_auth author (setUp)
        - sync GET request from auth user
        - sync POST request from unauth user
        - sync POST request from auth user
        - async GET request from auth user
        """
        url = reverse(
            'dictionary:change_status'
        )
        url_redirect = reverse('login') + '?next=' + url

        self.assertEqual(
            1, len(Dictionary.objects.all())
        )
        # sync GET request from auth and unauth user
        self.assertEqual(405, self.client_auth.get(url).status_code)
        self.assertEqual(302, self.client.get(url).status_code)
        self.assertEqual(url_redirect, self.client.get(url).url)

        payload = {
            'dictionary_pk': Dictionary.objects.latest('created').pk
        }

        # sync POST request from auth user
        res = self.client_auth.post(
            url,
            payload,
        )
        self.assertEqual(400, res.status_code)

        # sync POST request from unauth user
        res = self.client.post(
            url,
            payload,
        )
        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

        # async GET request from auth and unauth user return 405 status
        header = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        res = self.client_auth.get(
            url,
            payload,
            **header,
        )
        self.assertEqual(405, res.status_code)

        res = self.client.get(
            url,
            payload,
            **header,
        )
        self.assertEqual(302, res.status_code)

    def test_positive(self):
        """
        Testing positive result of changing status:
        - check status code 200;
        - check returned context;
        - check changing status in db;
        """
        url = reverse(
            'dictionary:change_status'
        )
        status = Dictionary.objects.latest('created').status
        payload = {
            'dictionary_pk': Dictionary.objects.latest('created').pk
        }
        header = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        res = self.client_auth.post(
            url,
            payload,
            **header,
        )
        self.assertEqual(200, res.status_code)
        self.assertIn("dictionary_status", res.content.decode())
        self.assertEqual(
            'private' if status == 'public' else 'public',
            Dictionary.objects.latest('created').status
        )

