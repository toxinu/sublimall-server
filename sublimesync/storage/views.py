# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.views.generic import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest

from .models import Member
from .models import Package


class APIView(View):
	http_method_names = ['post']

	def get_member(self, username, api_key):
		return Member.objects.get(user__username=username, api_key=api_key)

	@csrf_exempt
	def dispatch(self, *args, **kwargs):
		return super(APIView, self).dispatch(*args, **kwargs)


class UploadPackageAPIView(APIView):
	def post(self, request, *args, **kwargs):
		username = self.request.FILES.get('username')
		api_key = self.request.FILES.get('api_key')
		version = request.FILES.get('version')
		package = request.FILES.get('package')

		if not username or not api_key or not version or not package:
			return HttpResponseBadRequest()

		username = username.read()
		api_key = api_key.read()
		member = self.get_member(username, api_key)
		if not member:
			return HttpResponseForbidden()

		version = version.read()
		package = Package(
			member=member,
			version=version,
			package=package)
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
		if not member:
			return HttpResponseForbidden()

		package = Package.objects.get(
			member=member, version=version)

		if not package:
			return HttpResponseNotFound()

		response = HttpResponse(package.package.read(), mimetype='application/zip, application/octet-stream')
		response.streaming = True
		return response


class AccountView(TemplateView):
	template_name = 'account.html'