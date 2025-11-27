from django.conf import settings
from django.test import TestCase

from smllr.shorturls.models import ShortURL
from smllr.users.models import User


class ShortURLTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test", email="test@test.com")
        self.user.set_unusable_password()

    def test_anon_user_shorturl_limit(self):
        for i in range(settings.MAX_SHORTURLS_PER_ANON_USER):
            ShortURL.objects.create(
                user=self.user, destination_url="https://smllr.io", name=f"Test {i}"
            )

        with self.assertRaises(Exception) as ex:
            ShortURL.objects.create(
                user=self.user, destination_url="https://smllr.io", name="Error"
            )

        self.assertEqual(ex.exception.__str__(), "You've reached your limit of URLs.")
