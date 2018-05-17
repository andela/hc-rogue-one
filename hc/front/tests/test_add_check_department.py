from hc.api.models import Check, Department
from hc.test import BaseTestCase


class AddCheckToDepartmentTestCase(BaseTestCase):
    """ Test for addition of check to department """

    def test_check_add_to_department(self):
        """ Test that check can be added to department """
        self.client.login(username="alice@example.org", password="password")

        department = Department(user=self.alice, name="Marketing")
        department.save()
        check = Check(user=self.alice)
        check.save()

        form = {"name": "Cron 2"}
        url = "/checks/%s/name/" % check.code

        response = self.client.post(url, form)
        self.assertRedirects(response, "/checks/")
        check = Check.objects.get(code=check.code)
        self.assertEqual(check.name, "Cron 2")
