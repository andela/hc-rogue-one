from hc.api.models import Department
from hc.test import BaseTestCase


class AddDepartmentTestCase(BaseTestCase):
    """ Test for new department creation """

    def test_add_department_url_works(self):
        self.client.login(username="alice@example.org", password="password")

        response = self.client.get("/departments/add/")
        self.assertEqual(response.status_code, 200)

    def test_department_can_be_added(self):
        """ Test that new department can be created using URL """
        self.client.login(username="alice@example.org", password="password")

        self.client.get("/departments/add/")
        form = {"name": "Marketing"}
        response = self.client.post("/departments/add/", form)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Department.objects.filter(user=self.alice).count(), 1)
