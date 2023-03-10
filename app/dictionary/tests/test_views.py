import os

from django.conf import settings

from django.urls import reverse

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
            'AddStudentForm',
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
            'AddStudentForm',
            res.context_data.get('form').__class__.__name__
        )
