# -*- coding: utf-8 -*-
import json
from io import BytesIO
from unittest import skip
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

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

    def _get_post_data(
            self,
            fields=['email', 'api_key', 'version', 'package', 'platform', 'arch']):
        data = {}
        for attr in fields:
            c = BytesIO()
            c.name = attr
            data[attr] = c
        return data

    def _set(self, data, attr, value):
        value = str(value)

        data[attr] = BytesIO(bytes(value.encode('utf-8')))
        data[attr].name = attr
        return data

    def test_upload_with_bad_form(self):
        data = self._get_post_data(fields=['jambon'])

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)

    def test_upload_without_credentials(self):
        data = self._get_post_data()

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'], [
            'Email is mandatory.',
            'API key is mandatory.',
            'Version is mandatory.',
            'Package is mandatory.'])

    def test_upload_with_bad_credentials(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', 'teststs')
        self._set(data, 'version', 2)
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Package.objects.all().count(), 0)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'][0], 'Bad credentials.')

    def test_upload_without_version(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'][0], 'Version is mandatory.')

    def test_upload_with_bad_version(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 4)
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'][0], 'Bad version. Must be 2 or 3.')

        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 'a')
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'][0], 'Bad version. Must be 2 or 3.')

    def test_upload_two_packages_with_different_version(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Package.objects.all().count(), 1)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 3)
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Package.objects.all().count(), 2)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

    def test_upload_too_big_package(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10 * 3)

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)

    def test_upload_package_with_same_version(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        self.c.post(reverse('api-upload'), data=data)

        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        self.c.post(reverse('api-upload'), data=data)

    def test_download_package_with_bad_form(self):
        data = self._get_post_data(fields=['jambon'])

        r = self.c.post(reverse('api-download'), data=data)
        self.assertEqual(r.status_code, 400)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'], [
            'Email is mandatory.',
            'API key is mandatory.',
            'Version is mandatory.'])

    def test_download_package_with_bad_credentials(self):
        data = {
            'email': self.user.email,
            'api_key': 'test',
            'version': 2
        }

        r = self.c.post(reverse('api-download'), data=data)
        self.assertEqual(r.status_code, 403)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'], ['Bad credentials.'])

    def test_download_not_found_package(self):
        data = {
            'email': self.user.email,
            'api_key': self.member.api_key,
            'version': 2
        }

        r = self.c.post(reverse('api-download'), data=data)
        self.assertEqual(r.status_code, 404)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'], ['Package not found.'])

    @skip('Incomplete test')
    def test_download_package(self):
        data = self._get_post_data()
        self._set(data, 'email', self.user.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        self.c.post(reverse('api-upload'), data=data)

        data = {
            'email': self.user.email,
            'api_key': self.member.api_key,
            'version': 2
        }
