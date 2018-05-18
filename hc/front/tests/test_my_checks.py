from hc.api.models import Check, AssignedChecks, Department
from hc.test import BaseTestCase
from datetime import timedelta as td
from django.utils import timezone


class MyChecksTestCase(BaseTestCase):

    def setUp(self):
        super(MyChecksTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()
        Department.objects.create(user=self.alice, name="Sales")
        self.department = Department.objects.get(name="Sales")


    def test_it_works(self):
        assigned_checks = AssignedChecks(user=self.bob, team=self.profile, checks=self.check)
        assigned_checks.save()
        assert AssignedChecks.objects.count() == 1
        for email in ("alice@example.org", "bob@example.org"):
            self.client.login(username=email, password="password")
            r = self.client.get("/checks/")
            self.assertContains(r, "Alice Was Here", status_code=200)

    def test_it_shows_green_check(self):
        self.check.last_ping = timezone.now()
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-up")

        # Mobile
        self.assertContains(r, "label-success")

    def test_it_shows_red_check(self):
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-down")

        # Mobile
        self.assertContains(r, "label-danger")

    def test_it_shows_amber_check(self):
        self.check.last_ping = timezone.now() - td(days=1, minutes=30)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-grace")

        # Mobile
        self.assertContains(r, "label-warning")

    def test_it_shows_red_often_check(self):
        self.check.last_ping = timezone.now()
        self.check.status = "often"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-often")

        # Mobile
        self.assertContains(r, "label-danger")

    def test_list_by_department_valid(self):
        """ Test that departments can be listed using a valid id """
        self.client.login(username="alice@example.org", password="password")
        self.check.department_id = self.department.id
        self.check.save()
        response = self.client.get("/checks/?department=%s" % self.department.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Was Here")

    def test_list_by_department_invalid(self):
        """ Test that departments cannot be listed using an invalid id """
        self.client.login(username="alice@example.org", password="password")
        response = self.client.get("/checks/?department=drs4567")
        self.assertEqual(response.status_code, 404)

