# -*- coding: utf-8 -*-
import json
from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from .models import Package
from sublimall.mixins import APIMixin
from sublimall.mixins import LoginRequiredMixin


class UploadPackageAPIView(APIMixin, View):
    @transaction.commit_on_success
    def post(self, request, *args, **kwargs):
        email = request.FILES.get('email')
        api_key = request.FILES.get('api_key')
        version = request.FILES.get('version')
        platform = request.FILES.get('platform')
        arch = request.FILES.get('arch')
        package_file = request.FILES.get('package')
        package_size = None

        if email:
            email = email.read()
        if api_key:
            api_key = api_key.read()
        if version:
            version = version.read()
        if platform:
            platform = platform.read()
        if arch:
            arch = arch.read()
        if package_file:
            package_size = package_file.seek(0, 2)

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

        try:
            package = member.package_set.get(version=version)
        except Package.DoesNotExist:
            package = None

        if package:
            package.member = member
            package.version = version
            package.platform = platform
            package.arch = arch
            package.package = package_file
        else:
            package = Package(
                member=member,
                version=version,
                platform=platform,
                arch=arch,
                package=package_file)

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
