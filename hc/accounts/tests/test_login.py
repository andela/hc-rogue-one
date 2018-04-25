from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from hc.api.models import Check
from hc.accounts.models import Profile


class LoginTestCase(TestCase):
    def test_it_sends_link(self):
        check = Check()
        check.save()

        session = self.client.session
        session["welcome_code"] = str(check.code)
        session.save()

        form = {"email": "alice@example.org"}

        r = self.client.post("/accounts/login/", form)
        self.assertEqual(r.status_code, 302)


        ### Assert that a user was created
        result = User.objects.get(email=form['email'])
        self.assertEqual(result.email, form['email'])

        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')
        ### Assert contents of the email body
        self.assertIn('To log into healthchecks.io',mail.outbox[0].body)

        ### Assert that check is associated with the new user
        user = User.objects.get(email=form['email'])
        result = Check.objects.get(user=user)
        self.assertEqual(user, result.user)

        # Any other tests?
