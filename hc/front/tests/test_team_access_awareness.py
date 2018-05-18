from hc.test import BaseTestCase

class WelcomePageTestCase(BaseTestCase):

    def test_team_access_awareness(self):
        r = self.client.get("/")
        self.assertContains(r, "Create a team and manage checks as a team", status_code=200)