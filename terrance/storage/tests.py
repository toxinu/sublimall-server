# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from ..accounts.models import Member


class PluginAPITestCase(TestCase):
    def setUp(self):
        self.c = Client()


class PackageTestCase(TestCase):
    def setUp(self):
        user = User(username='foo@bar.com', email='foo@bar.com', is_active=False)
        user.set_password('foobar')
        user.save()

        self.member = Member(user=user)
        self.member.save()
