import os
import shutil

# import ipdb
from django.conf import settings

from django.test import TestCase
from django.test import Client

from django.contrib.auth.models import User
from django.urls import reverse

# from dictionary.models import Dictionary


class Settings(TestCase):
    """
    Base settings for all view tests
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = os.path.join(
            settings.BASE_DIR,
            'tests/tmp_media'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


class TestDictionary(Settings):
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

    def test_AddDictionaryView_unauth(self):
        """
        Testing redirect when unauthenticated try to access /upload URL
        """
        url = reverse(
            'upload_file'
        )
        url_redirect = '/login/?next=/upload/'

        res = self.client.get(url)

        self.assertEqual(302, res.status_code)
        self.assertEqual(url_redirect, res.url)

    # def test_AddDictionaryView_auth(self):
    #     """
    #     Testing creating dictionary by authenticated user on /upload URL
    #     """
    #     url = reverse(
    #         'upload_file'
    #     )
    #
    #     # testing GET request: status code 200,
    #     # form with file field is available
    #     res = self.client_auth.get(url)
    #     self.assertEqual(200, res.status_code)
    #     self.assertTrue(res.context.get('user').is_authenticated)
    #     self.assertIn(
    #         'file',
    #         res.context.get('form').fields.keys()
    #     )
    #
    #     # testing POST request: status code 302,
    #     # provided file saved in db
    #     sample_file = os.path.join(
    #         settings.BASE_DIR,
    #         'tests/sample_file/valid_dict_file.xml'
    #     )
    #
    #     with open(sample_file, 'rb') as fp:
    #         res = self.client_auth.post(
    #             url,
    #             {'note': 'test file', 'status': 'public', 'file': fp}
    #         )
    #     self.assertEqual(302, res.status_code)
    #     self.assertEqual('/my_dictionaries', res.url)
    #     self.assertEqual(1, len(Dictionary.objects.all()))
    #     self.assertEqual('test file', Dictionary.objects.get(pk=1).note)
    #     self.assertEqual(
    #       'Test 2022.07.13',
    #       Dictionary.objects.get(pk=1).title
    #     )


# class TestLesson(Settings):
#     def setUp(self):
#         user_authenticated = {
#             'username': 'test_user_2',
#             'email': 'user_2@example.com',
#             'password': 'testpass456',
#         }
#         self.user_auth = User.objects.create_user(**user_authenticated)
#         self.client_auth = Client()
#         self.client_auth.force_login(self.user_auth)
#
#         user = {
#             'username': 'test_user_1',
#             'email': 'user_1@example.com',
#             'password': 'testpass123',
#         }
#         self.user = User.objects.create_user(**user)
#
#         sample_file = os.path.join(
#             settings.BASE_DIR,
#             'tests/sample_file/valid_dict_file.xml'
#         )
#
#         with open(sample_file, 'rb') as fp:
#             res = self.client_auth.post(
#                 reverse('upload_file'),
#                 {'note': 'test file', 'status': 'public', 'file': fp}
#             )
#
#     def test_lesson(self):
#         url = reverse(
#             'lesson:lesson',
#             kwargs={
#                 'user_pk': self.user.pk,
#                 'dictionary_pk': Dictionary.objects.latest('created').pk
#             }
#         )
#         res = self.client_auth.get(url)
#         self.assertEqual(200, res.status_code)
#         # ipdb.set_trace()
