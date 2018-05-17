from hc.api.models import Department
from hc.test import BaseTestCase


class ListDepartmentTestCase(BaseTestCase):
    """ Test for department listing """

    def test_departments_can_be_listed(self):
        """ Test that added departments can be created listed """
        self.client.login(username="alice@example.org", password="password")

        departments = ["Department%d" % d for d in range(0, 5)]

        for department in departments:
            dept = Department(user=self.alice, name=department)
            dept.save()

        depts = Department.objects.all()

        handled_depts = []
        for dept in depts:
            handled_depts.append(dept.name)

        assert set(departments) == set(handled_depts)


