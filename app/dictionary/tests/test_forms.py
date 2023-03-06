import os

from django.conf import settings

from django.test import Client

from django.contrib.auth.models import User
from django.urls import reverse

from dictionary.models import Dictionary
from dictionary.tests.test_views import BaseTestSettings


class TestDictionary(BaseTestSettings):
    """
    Testcase for testing views of dictionary-app
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

    def test_DictionaryForm_invalid_extension(self):
        """
        Testing form uploading dictionary with invalid extension
        """
        url = reverse(
            'upload_file'
        )

        # testing POST request: status code 302,
        # provided file saved in db
        sample_file = os.path.join(
            settings.BASE_DIR,
            'dictionary/tests/sample_file/invalid_extension.jpg'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                url,
                {'note': 'invalid_extension', 'status': 'public', 'file': fp}
            )
        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(Dictionary.objects.all()))
        self.assertFalse(res.context.get('form').is_valid())
        self.assertTrue(res.context.get('form').is_bound)
        self.assertEqual(
            'Допустимые расширения словарей "xml" и "csv"',
            res.context.get('form').errors.get('file')[0],
        )
        # import ipdb; ipdb.set_trace()

    def test_DictionaryForm_invalid_structure(self):
        """
        Testing form uploading dictionary with invalid structure
        """
        url = reverse(
            'upload_file'
        )

        # testing POST request: status code 302,
        # provided file saved in db
        sample_file = os.path.join(
            settings.BASE_DIR,
            'dictionary/tests/sample_file/invalid_file.xml'
        )

        with open(sample_file, 'rb') as fp:
            res = self.client_auth.post(
                url,
                {'note': 'invalid_file', 'status': 'public', 'file': fp}
            )
        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(Dictionary.objects.all()))
        self.assertFalse(res.context.get('form').is_valid())
        self.assertTrue(res.context.get('form').is_bound)
        self.assertEqual(
            'Загруженный файл не был распознан',
            res.context.get('form').errors.get('file')[0],
        )
        # import ipdb; ipdb.set_trace()
