import os

from django.conf import settings
from django.urls import reverse

from core.tests.base_settings import BaseTestSettings
from dictionary.models import Dictionary


class TestDictionary(BaseTestSettings):
    """
    Testcase for testing views of dictionary-app
    """

    def test_DictionaryForm_invalid_extension(self):
        """
        Testing form uploading dictionary with invalid extension
        """
        url = reverse(
            'dictionary:upload_file'
        )

        # testing POST request: status code 302,
        # provided file saved in db
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/invalid_extension.jpg'
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
            'dictionary:upload_file'
        )

        # testing POST request: status code 302,
        # provided file saved in db
        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/invalid_file.xml'
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
