# -*- coding: utf-8 -*-
from unittest import skip
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
# from django.core.files import File
from django.core.urlresolvers import reverse
# from mock import Mock

from .models import Package
from ..accounts.models import Member

ONE_MB = 'a' * 1000 * 1000


class PluginAPITestCase(TestCase):
    def setUp(self):
        self.user = User(username="foo@bar.com", email="foo@bar.com")
        self.user.set_password('foobar')
        self.user.full_clean()
        self.user.save()

        self.member = Member(user=self.user)
        self.member.full_clean()
        self.member.save()

        self.c = Client()

    def test_upload_without_credentials(self):
        data = {
            'username': '',
            'api_key': '',
            'version': '',
            'package': ''
        }

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

    def test_upload_with_bad_credentials(self):
        data = {
            'username': 'foo@bar.com',
            'api_key': 'teststs',
            'version': '',
            'package': ''
        }

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

        data.update({'api_key': self.member.api_key[:-2] + 'te'})

    def test_upload_without_version(self):
        data = {
            'username': 'foo@bar.com',
            'api_key': self.member.api_key,
            'version': '',
            'package': ''
        }

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

    @skip('Not finished')
    def test_upload_too_big_package(self):
        data = {
            'name': 'dick',
            # 'username': Mock(spec=File, name='username').write('foo@bar.com'),
            # 'api_key': Mock(spec=File).write(self.member.api_key),
            # 'version': Mock(spec=File).write('0.1'),
            # 'package': Mock(spec=File).write(ONE_MB * 10)
        }
        #data['api_key'].name = 'api_key'
        #data['version'].name = 'version'
        #data['package'].name = 'package'
        r = self.c.post(reverse('api-upload'), data=data)

        print(r.content)
        self.assertEqual(r.status_code, 200)


class PackageTestCase(TestCase):
    def setUp(self):
        user = User(username='foo@bar.com', email='foo@bar.com', is_active=False)
        user.set_password('foobar')
        user.save()

        self.member = Member(user=user)
        self.member.save()
