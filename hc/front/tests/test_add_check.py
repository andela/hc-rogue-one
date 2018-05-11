from hc.api.models import Check
from hc.test import BaseTestCase


class AddCheckTestCase(BaseTestCase):

    def test_it_works(self):
        url = "/checks/add/"
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url)
        self.assertRedirects(r, "/checks/")
        assert Check.objects.count() == 1

    ### Test that team access works
    def test_that_team_access_works(self):
        url = "/checks/add/"
<<<<<<< HEAD
        self.client.login(username="bob@example.com", password="password")
=======

        self.client.login(username="bob@example.org", password="password")

>>>>>>> 2294b80da384f751404e83a3fee3aca70b3c6ef3
        r = self.client.post(url)
        self.assertRedirects(r, "/checks/")
        assert Check.objects.count() == 1
