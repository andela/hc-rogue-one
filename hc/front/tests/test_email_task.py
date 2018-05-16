from hc.front.models import EmailTasks
from hc.test import BaseTestCase


class EmailTaskTestCase(BaseTestCase):

    def test_it_works(self):
        url = "/task/"
        self.client.login(username="alice@example.org", password="password")
        form = {"task_name":"reminder", "subject":"sub expriration", "recipients":"alice@example.org",
          "message":"hello there", "interval":1, "time":1}
        r = self.client.post(url, form)
        self.assertEqual(r.status_code, 200)

