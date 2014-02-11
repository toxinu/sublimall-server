# -*- coding: utf-8 -*-
import json
from io import BytesIO
from unittest import skip
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from .models import Package
from ..accounts.models import Member

ONE_MB = 'a' * 1000 * 1000


class PluginAPITestCase(TestCase):
    def setUp(self):
        self.member = Member(email="foo@bar.com", is_active=True)
        self.member.set_password('foobar')
        self.member.full_clean()
        self.member.save()

        self.c = Client()

    def _get_post_data(
            self,
            fields=['email', 'api_key', 'version', 'package', 'platform', 'arch']):
        """
        Generate a bytes dict for upload form
        """
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
        """
        Upload with a bad form on API
        """
        data = self._get_post_data(fields=['jambon'])

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)

    def test_upload_without_credentials(self):
        """
        Upload without credentials on API
        """
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
        """
        Upload with bad credentials on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
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
        """
        Upload without version on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Package.objects.all().count(), 0)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'][0], 'Version is mandatory.')

    def test_upload_with_bad_version(self):
        """
        Upload with incorrect version on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
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
        self._set(data, 'email', self.member.email)
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
        """
        Upload two packages with two different version on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Package.objects.all().count(), 1)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 3)
        self._set(data, 'package', 'content')

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Package.objects.all().count(), 2)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

    def test_upload_too_big_package(self):
        """
        Upload a too big package on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10 * 3)

        r = self.c.post(reverse('api-upload'), data=data)
        self.assertEqual(r.status_code, 400)

    def test_upload_package_with_same_version(self):
        """
        Upload two packages with same version on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        self.c.post(reverse('api-upload'), data=data)

        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        self.c.post(reverse('api-upload'), data=data)

        self.assertEqual(Package.objects.all().count(), 1)

    def test_download_package_with_bad_form(self):
        """
        Download a package with a bad form on API
        """
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
        """
        Download a package with bad credentials on API
        """
        data = {
            'email': self.member.email,
            'api_key': 'test',
            'version': 2
        }

        r = self.c.post(reverse('api-download'), data=data)
        self.assertEqual(r.status_code, 403)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'], ['Bad credentials.'])

    def test_download_not_found_package(self):
        """
        Download a package which doesn't exists on API
        """
        data = {
            'email': self.member.email,
            'api_key': self.member.api_key,
            'version': 2
        }

        r = self.c.post(reverse('api-download'), data=data)
        self.assertEqual(r.status_code, 404)

        j = json.loads(r.content.decode('utf-8'))
        self.assertFalse(j['success'])
        self.assertEqual(j['errors'], ['Package not found.'])

    @skip('incomplete test')
    def test_download_package(self):
        """
        Download a package on API
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        self.c.post(reverse('api-upload'), data=data)

        data = {
            'email': self.member.email,
            'api_key': self.member.api_key,
            'version': 2
        }

    def test_get_delete_package_not_logged(self):
        """
        Get request on delete package page without logged
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        r = self.c.get(reverse('delete-package', args=[p[0].pk]))
        self.assertEqual(r.status_code, 302)

    def test_get_delete_not_exists_package_not_logged(self):
        """
        Get request on delete package page without logged and package doesn't exists
        """
        r = self.c.get(reverse('delete-package', args=[6]))
        self.assertEqual(r.status_code, 302)

    def test_get_delete_package_logged(self):
        """
        Get request on delete package page logged
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        self.c.login(email=self.member.email, password='foobar')
        r = self.c.get(reverse('delete-package', args=[p[0].pk]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['package'].id, p[0].pk)

    def test_get_delete_package_not_exists_logged(self):
        """
        Get request on delete package page logged but package doesn't exists
        """
        self.c.login(email=self.member.email, password='foobar')
        r = self.c.get(reverse('delete-package', args=[6]))
        self.assertEqual(r.status_code, 302)

    def test_get_delete_package_not_owned_logged(self):
        """
        Get request on delete package page logged but package not owned
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        m = Member(email="foo2@bar.com", is_active=True)
        m.set_password('foobar')
        m.full_clean()
        m.save()

        self.c.login(email=m.email, password='foobar')
        r = self.c.get(reverse('delete-package', args=[p[0].pk]))
        self.assertEqual(r.status_code, 302)

        self.assertEqual(self.member.package_set.all().count(), 1)

    def test_post_delete_package_not_logged(self):
        """
        Post request on delete package page not logged
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        r = self.c.post(reverse('delete-package', args=[p[0].pk]))
        self.assertEqual(r.status_code, 302)

        self.assertEqual(Package.objects.all().count(), 1)

    def test_post_delete_not_exists_package_not_logged(self):
        """
        Post request on delete package which doesn't exist and not logged
        """
        r = self.c.post(reverse('delete-package', args=[15]))
        self.assertEqual(r.status_code, 302)

        self.assertEqual(Package.objects.all().count(), 0)

    def test_post_delete_package_not_exists_logged(self):
        """
        Post request on delete package which doesn't exists and logged
        """
        self.c.login(email=self.member.email, password='foobar')
        r = self.c.post(reverse('delete-package', args=[15]))
        self.assertEqual(r.status_code, 302)

        self.assertEqual(Package.objects.all().count(), 0)

    def test_post_delete_package_not_owned_logged(self):
        """
        Post request on delete package page which doesn't owned and logged
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        m = Member.objects.create_user(email='foo2@bar.com', password='foobar')

        self.c.login(email=m.email, password='foobar')
        r = self.c.post(reverse('delete-package', args=[p[0].pk]))
        self.assertEqual(r.status_code, 302)

        self.assertEqual(Package.objects.all().count(), 1)

    def test_post_delete_package_logged(self):
        """
        Post request on delete package page logged
        """
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        self.c.login(email=self.member.email, password='foobar')
        r = self.c.post(reverse('delete-package', args=[p[0].pk]))
        self.assertEqual(r.status_code, 302)


class PackageTestCase(TestCase):
    def setUp(self):
        self.member = Member(email="foo@bar.com", is_active=True)
        self.member.set_password('foobar')
        self.member.full_clean()
        self.member.save()

        self.c = Client()

    def _get_post_data(
            self,
            fields=['email', 'api_key', 'version', 'package', 'platform', 'arch']):
        """
        Generate a bytes dict for upload form
        """
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

    def test_package_representation(self):
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        self.assertEqual(p[0].__unicode__(), self.member.email)
        self.assertEqual(p[0].__str__(), self.member.email)

    def test_package_size_property(self):
        data = self._get_post_data()
        self._set(data, 'email', self.member.email)
        self._set(data, 'api_key', self.member.api_key)
        self._set(data, 'version', 2)
        self._set(data, 'package', ONE_MB * 10)

        r = self.c.post(reverse('api-upload'), data=data)
        j = json.loads(r.content.decode('utf-8'))
        self.assertTrue(j['success'])

        p = self.member.package_set.all()

        self.assertEqual(p[0].size, 10 * 1000 * 1000)
