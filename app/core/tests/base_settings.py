import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model

from django.test import TestCase
from django.test import Client


class BaseTestSettings(TestCase):
    """
    Base settings for all view tests
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = os.path.join(
            settings.BASE_DIR,
            'core/tests/tmp_media'
        )
        user = {
            'username': 'test_user_1',
            'email': 'user_1@example.com',
            'password': 'testpass123',
        }
        cls.user = get_user_model().objects.create_user(**user)

        user_authenticated = {
            'username': 'test_user_2',
            'email': 'user_2@example.com',
            'password': 'testpass456',
        }
        cls.user_auth = get_user_model() \
            .objects.create_user(**user_authenticated)
        cls.client_auth = Client()
        cls.client_auth.force_login(cls.user_auth)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
