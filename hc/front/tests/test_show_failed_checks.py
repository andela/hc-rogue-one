from hc.api.models import Check
from hc.test import BaseTestCase
from datetime import timedelta as td
from django.utils import timezone
from hc.front.views import my_failed_checks


class MyFailedChecksTestCase(BaseTestCase):

    def setUp(self):
        super(MyFailedChecksTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()

    def test_url_works(self):
        """ Test if the url to show failed checks works """
        for email in ("alice@example.org", "bob@example.org"):
                self.client.login(username=email, password="password")
        r = self.client.get("/checks/failed/")
        self.assertEqual(r.status_code, 200)

    def test_it_shows_only_failed_checks(self):
        """ Test if  show failed checks view function works """
        self.check.last_ping = timezone.now() - td(days=1, minutes=30)
        self.check.status = "down"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/failed/")
        self.assertContains(r, "text")
