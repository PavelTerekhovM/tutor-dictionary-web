import os

from django.conf import settings

from core.tests.base_settings import BaseTestSettings
from dictionary.helpers import DictionaryFileManager
from dictionary.models import Dictionary


class TestDictionary(BaseTestSettings):
    """
    Testcase for testing views of dictionary-app
    """

    def test_DictionaryFileManager_clean_valid_xml(self):
        """
        Testing helper which handling uploaded valid xml files
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file.xml'
        )
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.clean_file()
        self.assertIsNotNone(res)
        self.assertEqual(sample_file, res.name)

    def test_DictionaryFileManager_invalid_extension_file(self):
        """
        Testing helper which handling uploaded file with invalid extension
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/invalid_extension.jpg'
        )
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.clean_file()
        self.assertIsNone(res)

    def test_DictionaryFileManager_invalid_xml(self):
        """
        Testing helper which handling uploaded invalid xml dictionary
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/invalid_file.xml'
        )
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.clean_file()

        self.assertIsNone(res)

    def test_DictionaryFileManager_valid_file_without_title(self):
        """
        Testing helper which handling uploaded valid file without title
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file_without_name.xml'
        )

        obj = Dictionary.objects.create(author=self.user)
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.parse_file(obj=obj)

        self.assertIsNotNone(res)
        self.assertEqual(1, len(Dictionary.objects.all()))
        self.assertEqual(
            'Без имени',
            Dictionary.objects.latest('created').title
        )

    def test_DictionaryFileManager_csv_file(self):
        """
        Testing helper which handling uploaded invalid csv_file
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/csv_file.csv'
        )

        obj = Dictionary.objects.create(author=self.user)
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.parse_file(obj=obj)

        self.assertIsNone(res)

    def test_DictionaryFileManager_parse_valid_xml(self):
        """
        Testing helper which handling uploaded valid xml files
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file.xml'
        )
        obj = Dictionary.objects.create(author=self.user)
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.parse_file(obj=obj)

        # check number of inserted words, title, and slug
        self.assertIsNotNone(res)
        self.assertEqual(25, res.word.count())
        self.assertEqual('Test 2022.07.13', res.title)
        self.assertEqual('test-2022-07-13', res.slug)

    def test_DictionaryFileManager_parse_without_title(self):
        """
        Testing helper which handling uploaded valid xml files
        """

        sample_file = os.path.join(
            settings.BASE_DIR,
            'core/tests/sample_file/valid_dict_file_without_name.xml'
        )
        obj = Dictionary.objects.create(author=self.user)
        with open(sample_file, 'rb') as file:
            instance = DictionaryFileManager(file)
            res = instance.parse_file(obj=obj)

        # check number of inserted words, title, and slug
        self.assertIsNotNone(res)
        self.assertEqual(25, res.word.count())
        self.assertEqual('Без имени', res.title)
        self.assertEqual('bez-imeni', res.slug)

# import ipdb; ipdb.set_trace()
