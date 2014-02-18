# -*- coding: utf-8 -*-
import os
import json
from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.files import File
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

from .models import Package
from sublimall.mixins import APIMixin
from sublimall.mixins import LoginRequiredMixin


class UploadPackageAPIView(APIMixin, View):
    @transaction.commit_on_success
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        api_key = request.POST.get('api_key')
        version = request.POST.get('version')
        platform = request.POST.get('platform')
        arch = request.POST.get('arch')
        package_content = request.POST.get('package')
        package_size = len(package_content.encode('utf-8'))

        if not email or not api_key or not package_size or not version:
            message = {'success': False, 'errors': []}
            if not email:
                message['errors'].append('Email is mandatory.')
            if not api_key:
                message['errors'].append('API key is mandatory.')
            if not version:
                message['errors'].append('Version is mandatory.')
            if not package_size:
                message['errors'].append('Package is mandatory.')
            return HttpResponseBadRequest(json.dumps(message))

        member = self.get_member(email, api_key)
        if member is None:
            return HttpResponseForbidden(
                json.dumps({'success': False, 'errors': ['Bad credentials.']}))

        try:
            version = int(version)
        except ValueError:
            return HttpResponseBadRequest(
                json.dumps(
                    {'success': False, 'errors': ['Bad version. Must be 2 or 3.']}))

        if version not in [2, 3]:
            return HttpResponseBadRequest(
                json.dumps(
                    {'success': False, 'errors': ['Bad version. Must be 2 or 3.']}))

        upload_to_path = os.path.join(
            default_storage.location, settings.PACKAGES_UPLOAD_TO)

        if not os.path.exists(upload_to_path):
            os.makedirs(upload_to_path)

        try:
            package = member.package_set.get(version=version)
        except Package.DoesNotExist:
            package = None

        if package:
            print('*** 1')
            package.member = member
            package.version = version
            package.platform = platform
            package.arch = arch
        else:
            print('*** 2')
            package = Package(
                member=member,
                version=version,
                platform=platform,
                arch=arch)



        if package.package and default_storage.exists(package.package.path):
            print('*** 3')
            package.package.file.open('wb')
            package.package.file.write(package_content.encode('utf-8'))
        else:
            print('*** 4')
            package.full_clean()
            package.save()
            package_path = default_storage.save(
                os.path.join(upload_to_path, 'package_%s' % package.pk),
                ContentFile(package_content))
            package_file = File(default_storage.open(package_path))
            package.package = package_file
            package.path = package_path

        try:
            package.full_clean()
        except ValidationError as err:
            return HttpResponseBadRequest(
                json.dumps(
                    {'success': False, 'errors': err.messages}))

        package.save()

        return HttpResponse(json.dumps({'success': True}), status=201)


class DownloadPackageAPIView(APIMixin, View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        api_key = request.POST.get('api_key')
        version = request.POST.get('version')

        if not email or not api_key and not version:
            message = {'success': False, 'errors': []}
            if not email:
                message['errors'].append('Email is mandatory.')
            if not api_key:
                message['errors'].append('API key is mandatory.')
            if not version:
                message['errors'].append('Version is mandatory.')
            return HttpResponseBadRequest(json.dumps(message))

        member = self.get_member(email, api_key)
        if member is None:
            return HttpResponseForbidden(
                json.dumps({'success': False, 'errors': ['Bad credentials.']}))

        try:
            package = member.package_set.get(version=version)
        except Package.DoesNotExist:
            return HttpResponseNotFound(
                json.dumps({'success': False, 'errors': ['Package not found.']}))

        response = HttpResponse(
            package.package.read(), mimetype='application/zip, application/octet-stream')
        response.streaming = True
        response['Content-Disposition'] = 'attachment; filename=package_version-%s.zip' \
            % package.version
        return response


class DeletePackageView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        try:
            package = request.user.package_set.get(pk=kwargs.get('pk'))
        except Package.DoesNotExist:
            return HttpResponseRedirect(reverse('account'))
        return render(request, 'package-delete.html', {'package': package})

    def post(self, request, pk):
        try:
            package = request.user.package_set.get(pk=pk)
        except Package.DoesNotExist:
            return HttpResponseRedirect(reverse('account'))

        package.delete()
        return HttpResponseRedirect(reverse('account'))


class DeletePackageAPIView(APIMixin, View):
    def post(self, request):
        email = request.POST.get('email')
        api_key = request.POST.get('api_key')
        version = request.POST.get('version')

        if not email or not api_key or not version:
            message = {'success': False, 'errors': []}
            if not email:
                message['errors'].append('Email is mandatory.')
            if not api_key:
                message['errors'].append('API key is mandatory.')
            if not version:
                message['errors'].append('Version is mandatory.')
            return HttpResponseBadRequest(json.dumps(message))

        member = self.get_member(email, api_key)
        if member is None:
            return HttpResponseForbidden(
                json.dumps({'success': False, 'errors': ['Bad credentials.']}))

        try:
            package = member.package_set.filter(version=version)
        except Package.DoesNotExist:
            return HttpResponseNotFound(
                json.dumps({'success': False, 'errors': ['Package not found.']}))

        package.delete()
        return HttpResponse({'success': True})


class MaxPackageSizeAPIView(APIMixin, View):
    def post(self, request):
        email = request.POST.get('email')

        api_key = request.POST.get('api_key')
        if not email or not api_key:
            message = {'success': False, 'errors': []}
            if not email:
                message['errors'].append('Email is mandatory.')
            if not api_key:
                message['errors'].append('API key is mandatory.')
            return HttpResponseBadRequest(json.dumps(message))

        member = self.get_member(email, api_key)
        if member is None:
            return HttpResponseForbidden(
                json.dumps({'success': False, 'errors': ['Bad credentials.']}))

        return HttpResponse({'success': True, 'output': settings.MAX_PACKAGE_SIZE})
