# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .utils import get_hash

from .models import Member


class UtilsTestCase(TestCase):
    def test_get_hash_length(self):
        """
        Hash generator must return 40 characters
        """
        self.assertEqual(len(get_hash()), 40)


class PluginAPITestCase(TestCase):
    def setUp(self):
        self.c = Client()


class RedirectionTestCase(TestCase):
    def setUp(self):
        self.c = Client()

        self.user = User(username="foo@bar.com", email="foo@bar.com")
        self.user.set_password("foobar")
        self.user.save()

        member = Member(user=self.user)
        member.save()

    def test_account_not_logged(self):
        """
        Access Account page while not logged
        """
        r = self.c.get(reverse('account'))
        self.assertEqual(r.status_code, 302)

    def test_logout_not_logged(self):
        """
        Access Logout page while not logged
        """
        r = self.c.get(reverse('logout'))
        self.assertEqual(r.status_code, 302)

    def test_new_api_key_not_logged(self):
        """
        Generate new api key while not logged
        """
        r = self.c.get(reverse('account-new-api-key'))
        self.assertEqual(r.status_code, 302)

    def test_registration_logged(self):
        """
        Access registration page while logged
        """
        self.c.login(username=self.user.username, password="foobar")

        r = self.c.get(reverse('registration'))
        self.assertEqual(r.status_code, 302)

    def test_login_logged(self):
        """
        Access login page while logged
        """
        self.c.login(username=self.user.username, password="foobar")

        r = self.c.get(reverse('login'))
        self.assertEqual(r.status_code, 302)

    def test_new_api_key_logged(self):
        """
        Access new api key page while logged
        """
        self.c.login(username=self.user.username, password="foobar")

        r = self.c.get(reverse('account-new-api-key'))
        self.assertEqual(r.status_code, 302)


class MemberTestCase(TestCase):
    def setUp(self):
        user = User(username='foo@bar.com', email='foo@bar.com')
        user.set_password('foobar')
        user.save()

        self.member = Member(user=user)
        self.member.save()

        self.c = Client()

    def test_member_default_api_key(self):
        """
        Member object must have a default api key
        """
        self.assertEqual(len(self.member.api_key), 40)

    def test_member_new_api_key_logged(self):
        """
        Member must have new api key after a GET on new api page
        """
        self.c.login(username='foo@bar.com', password='foobar')
        r = self.c.get(reverse('account-new-api-key'))
        self.assertEqual(r.status_code, 302)

        member = Member.objects.get(user=self.member.user)
        self.assertNotEqual(self.member.api_key, member.api_key)


class RegistrationTestCase(TestCase):
    pass


class PackageTestCase(TestCase):
    def setUp(self):
        user = User(username='foo@bar.com', email='foo@bar.com', is_active=False)
        user.set_password('foobar')
        user.save()

        self.member = Member(user=user)
        self.member.save()
