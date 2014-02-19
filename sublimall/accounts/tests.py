# -*- coding: utf-8 -*-
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from .utils import get_hash
from .models import Member


class UtilsTestCase(TestCase):
    def test_get_hash_length(self):
        """
        Hash generator must return 40 characters
        """
        self.assertEqual(len(get_hash()), 40)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.member = Member(email="foo@bar.com")
        self.member.set_password("foobar")
        self.member.save()

    def test_access_registration_not_logged(self):
        """
        Access login page while not logged
        """
        r = self.c.get(reverse('registration'))
        self.assertEqual(r.status_code, 200)

    def test_access_login_not_logged(self):
        """
        Access login page while not logged
        """
        r = self.c.get(reverse('login'))
        self.assertEqual(r.status_code, 200)

    def test_access_account_not_logged(self):
        """
        Access Account page while not logged
        """
        r = self.c.get(reverse('account'))
        self.assertEqual(r.status_code, 302)

    def test_access_logout_not_logged(self):
        """
        Access Logout page while not logged
        """
        r = self.c.get(reverse('logout'))
        self.assertEqual(r.status_code, 302)

    def test_access_new_api_key_not_logged(self):
        """
        Generate new api key while not logged
        """
        r = self.c.get(reverse('account-new-api-key'))
        self.assertEqual(r.status_code, 302)

    def test_access_registration_logged(self):
        """
        Access registration page while logged
        """
        self.member.is_active = True
        self.member.save()

        self.c.login(email=self.member.email, password="foobar")

        r = self.c.get(reverse('registration'))
        self.assertEqual(r.status_code, 302)

    def test_access_login_logged(self):
        """
        Access login page while logged
        """
        self.member.is_active = True
        self.member.save()

        self.c.login(email=self.member.email, password="foobar")

        r = self.c.get(reverse('login'))
        self.assertEqual(r.status_code, 302)

    def test_access_new_api_key_logged(self):
        """
        Access new api key page while logged
        """
        self.member.is_active = True
        self.member.save()

        self.c.login(email=self.member.email, password="foobar")

        r = self.c.get(reverse('account-new-api-key'))
        self.assertEqual(r.status_code, 302)

    def test_access_account_logged(self):
        """
        Access account page while logged
        """
        self.member.is_active = True
        self.member.save()

        self.c.login(email=self.member.email, password="foobar")

        r = self.c.get(reverse('account'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['email'], self.member.email)
        self.assertEqual(r.context['api_key'], self.member.api_key)


class MemberTestCase(TestCase):
    def setUp(self):
        self.member = Member(email="foo@bar.com")
        self.member.set_password('foobar')
        self.member.save()

        self.c = Client()

    def test_member_repr(self):
        """
        Member object representation
        """
        self.assertEqual(self.member.__unicode__(), self.member.email)
        self.assertEqual(self.member.__str__(), self.member.email)

    def test_member_get_full_name(self):
        """
        Member object get_full_name method
        """
        self.assertEqual(self.member.get_full_name(), self.member.email)

    def test_member_get_short_name(self):
        """
        Member object get_short_name method
        """
        self.assertEqual(self.member.get_short_name(), self.member.email)

    def test_member_create_superuser(self):
        """
        MemberManager create_superuser method
        """
        m = Member.objects.create_superuser(email="foo2@bar.com", password="foobar")
        self.assertTrue(m.is_superuser)

    def test_member_create_user(self):
        """
        MemberManager create_user method
        """
        m = Member.objects.create_user(email="foo2@bar.com", password="foobar")
        self.assertTrue(m.is_active)

        self.assertRaises(ValueError, Member.objects.create_user, password="foobar")

    def test_member_default_api_key(self):
        """
        Member object must have a default api key
        """
        self.assertEqual(len(self.member.api_key), 40)

    def test_member_new_api_key_logged(self):
        """
        Member must have new api key after a GET on new api page
        """
        self.member.is_active = True
        self.member.save()

        self.c.login(email='foo@bar.com', password='foobar')

        r = self.c.get(reverse('account-new-api-key'))
        self.assertEqual(r.status_code, 302)

        member = Member.objects.get(pk=self.member.pk)
        self.assertNotEqual(self.member.api_key, member.api_key)


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def test_registration_default_key(self):
        m = Member(email='foo@bar.com')
        m.set_password('foobar')
        m.save()

        self.assertTrue(m.registration_key)

    def test_invalid_email(self):
        """
        Email validation
        """
        data = {
            'email': '',
            'email2': '',
            'password': 'foobar123',
            'password2': 'foobar123'}

        # Empty email
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form']['errors'], "Email can't be empty.")

        # Not same emails
        data.update({'email': 'foo@bar.com', 'email2': 'foo@bar2.com'})
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form']['errors'], "Emails doesn't match.")

        # Invalid email
        data.update({'email': 'foo@bar', 'email2': 'foo@bar'})
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form']['errors'], "Need a valid email.")

    def test_invalid_password(self):
        """
        Password validation
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': '',
            'password2': ''
        }

        # Empty password
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form']['errors'], "Password can't be empty.")

        # Not same valid password
        data.update({'password': 'foobar123', 'password2': 'foobar1234'})
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form']['errors'], "Password doesn't match.")

        # Without numerical character
        data.update({'password': 'foobar', 'password2': 'foobarr'})
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.context['form']['errors'],
            "Need at least one numerical character in password.")

        # Less than 5 characters
        data.update({'password': 'test', 'password2': 'test'})
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.context['form']['errors'],
            "Need at least 6 characters for your password.")

        # Without alpha character
        data.update({'password': '123123', 'password2': '123123"'})
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.context['form']['errors'],
            "Need at least one alpha character in password.")

    def test_new_member(self):
        """
        Registration object must have a default key
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Member.objects.all().count(), 1)
        member = Member.objects.get(email='foo@bar.com')
        self.assertTrue(member.check_password('foobar123'))
        self.assertFalse(member.is_active)

    def test_email_already_exists(self):
        """
        Registration with an email that already exists
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)
        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["form"]["errors"], "Email already used.")

    def test_confirmation_mail(self):
        """
        Registration must send an email with validation link
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['foo@bar.com'])

        member = Member.objects.get(email=data.get('email'))

        validation = '%s/%s' % (
            member.id, member.registration_key) in mail.outbox[0].body
        self.assertTrue(validation)

    def test_registration_confirmation(self):
        """
        Validate registration
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)

        member = Member.objects.get(email=data.get('email'))

        r = self.c.get(reverse(
            'registration-confirmation',
            args=[member.id, member.registration_key]))
        self.assertEqual(r.status_code, 302)

        member = Member.objects.get(pk=member.pk)
        self.assertTrue(member.is_active)

        member = Member.objects.get(email="foo@bar.com")
        self.assertTrue(member.is_active)

    def test_registration_confirmation_invalid_pk(self):
        """
        Validate registration with bad pk
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)

        member = Member.objects.get(email=data.get('email'))

        r = self.c.get(reverse(
            'registration-confirmation', args=[100, member.registration_key]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['error'], 'Invalid key or account already active.')

        member = Member.objects.get(email=data.get('email'))
        self.assertFalse(member.is_active)

    def test_registration_confirmation_bad_key(self):
        """
        Validate registration with bad key
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)

        member = Member.objects.get(email=data.get('email'))

        r = self.c.get(reverse(
            'registration-confirmation',
            args=[member.id, member.registration_key[:-4] + "test"]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['error'], 'Invalid key or account already active.')

        self.assertFalse(member.is_active)

    def test_inactive_member_login(self):
        """
        Inactive member can't log in without validate registration
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)
        r = self.c.post(
            reverse('login'), {'username': 'foo@bar.com', 'password': 'foobar123'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.context['form'].errors['__all__'][0], 'This account is inactive.')
        self.assertFalse(self.c.session.get('_auth_user_id', False))

    def test_login_active_member(self):
        """
        Login with active member
        """
        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }
        self.c.post(reverse('registration'), data)

        member = Member.objects.get(email=data.get('email'))

        r = self.c.get(reverse(
            'registration-confirmation',
            args=[member.id, member.registration_key]))
        r = self.c.post(
            reverse('login'),
            {'username': data.get('email'), 'password': data.get('password')})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(self.c.session.get('_auth_user_id', False))

    def test_max_registration_reach(self):
        old_MAX_MEMBER = settings.MAX_MEMBER
        settings.MAX_MEMBER = 5
        for i in range(0, settings.MAX_MEMBER):
            Member.objects.create_user(email="foo%s@bar.com" % i, password="foobar")

        r = self.c.get(reverse('registration'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['title'], 'Max registration reach')

        data = {
            'email': 'foo@bar.com',
            'email2': 'foo@bar.com',
            'password': 'foobar123',
            'password2': 'foobar123'
        }

        r = self.c.post(reverse('registration'), data)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Member.objects.filter(email='foo@bar.com').exists())
        settings.MAX_MEMBER = old_MAX_MEMBER
