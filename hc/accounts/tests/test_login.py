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
<<<<<<< HEAD
        assert User.objects.get(email=form['email'])
        
=======
        result = User.objects.get(email=form['email'])
        self.assertEqual(result.email, form['email'])
>>>>>>> 2294b80da384f751404e83a3fee3aca70b3c6ef3

        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')
        
        ### Assert contents of the email body
        self.assertIn('To log into healthchecks.io',mail.outbox[0].body)

        ### Assert that check is associated with the new user
        user = User.objects.get(email=form['email'])
<<<<<<< HEAD
<<<<<<< ecf0b40b8bb5ad0954dcfba1c652405b0758ec19
        result = Check.objects.get(user=user)
        self.assertEqual(user, result.user)
=======
        assert(Check.objects.get(user=user))
>>>>>>> Fixing accounts tests
=======
        result = Check.objects.get(user=user)
        self.assertEqual(user, result.user)
>>>>>>> 2294b80da384f751404e83a3fee3aca70b3c6ef3

    def test_it_pops_bad_link_from_session(self):
        self.client.session["bad_link"] = True
        self.client.get("/accounts/login/")
        assert "bad_link" not in self.client.session

        ### Any other tests?

