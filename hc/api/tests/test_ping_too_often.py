from django.test import Client, TestCase

from hc.api.models import Check, Ping


class TryTestCase(TestCase):

    def setUp(self):
        super(TryTestCase, self).setUp()
        self.check = Check.objects.create()

    def test_it_works(self):
        r = self.client.get("/ping/%s/" % self.check.code)
        assert r.status_code == 200

        self.check.refresh_from_db()
        assert self.check.status == "up"

        r = self.client.get("/ping/%s/" % self.check.code)
        self.check.refresh_from_db()
        assert self.check.status == "often"

        print(self.check.status)