# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from .models import Package
from ..accounts.models import Member


class APIView(View):
    http_method_names = ['post']

    def get_member(self, username, api_key):
        try:
            return Member.objects.get(user__username=username, api_key=api_key)
        except Member.DoesNotExist:
            return None

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(APIView, self).dispatch(*args, **kwargs)


class UploadPackageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.FILES.get('username')
        api_key = request.FILES.get('api_key')
        version = request.FILES.get('version')
        platform = request.FILES.get('platform')
        arch = request.FILES.get('arch')
        package = request.FILES.get('package')

        if not username or not api_key or not package or not version:
            message = {'success': False, 'errors': []}
            if not username:
                message['errors'].append('Username is mandatory.')
            if not api_key:
                message['errors'].append('API key is mandatory.')
            if not version:
                message['errors'].append('Version is mandatory.')
            if not package:
                message['errors'].append('Package is mandatory.')
            return HttpResponseBadRequest(json.dumps(message))

        username = username.read()
        api_key = api_key.read()
        member = self.get_member(username, api_key)
        if member is None:
            return HttpResponseForbidden()

        if platform:
            platform = platform.read()
        if arch:
            arch = arch.read()

        version = version.read()
        package = Package(
            member=member,
            version=version,
            platform=platform,
            arch=arch,
            package=package)
        package.full_clean()
        package.save()

        old_package = Package.objects.exclude(id=package.id).filter(
            member=member, version=version)
        if old_package.exists():
            old_package.delete()

        return HttpResponse(201)


class DownloadPackageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        api_key = request.POST.get('api_key')
        version = request.POST.get('version')

        if not username or not api_key and not version:
            return HttpResponseBadRequest()

        member = self.get_member(username, api_key)
        if member is None:
            return HttpResponseForbidden()

        package = Package.objects.get(
            member=member, version=version)

        if not package:
            return HttpResponseNotFound()

        response = HttpResponse(package.package.read(), mimetype='application/zip, application/octet-stream')
        response.streaming = True
        return response
