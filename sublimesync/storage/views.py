# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest

from .models import Member
from .models import Package
from django.contrib.auth.models import User


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
        username = self.request.FILES.get('username')
        api_key = self.request.FILES.get('api_key')
        version = request.FILES.get('version')
        package = request.FILES.get('package')

        if not username or not api_key or not version or not package:
            return HttpResponseBadRequest()

        username = username.read()
        api_key = api_key.read()
        member = self.get_member(username, api_key)
        if member is None:
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
        if member is None:
            return HttpResponseForbidden()

        package = Package.objects.get(
            member=member, version=version)

        if not package:
            return HttpResponseNotFound()

        response = HttpResponse(package.package.read(), mimetype='application/zip, application/octet-stream')
        response.streaming = True
        return response


class RegistrationView(View):
    http_method_names = ['get', 'post']

    def get(self, request):
        return render(request, 'registration.html')

    @transaction.commit_on_success
    def post(self, request):
        template = 'registration.html'

        email = request.POST.get('email')
        email2 = request.POST.get('email2')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not email:
            return render(request, template, {"form": {'errors': "Email can't be empty."}})
        if not password:
            return render(request, template, {"form": {'errors': "Password can't be empty."}})

        try:
            validate_email(email)
        except ValidationError:
            return render(request, template, {"form": {'errors': "Need a valid email."}})

        if len(password) <= 5:
            return render(
                request,
                template,
                {"form": {'errors': "Need at least 6 characters for your password."}})

        if not any(char.isalpha() for char in password):
            return render(
                request,
                template,
                {"form": {'errors': "Need at least one alpha character in password."}})

        if not any(char.isdigit() for char in password):
            return render(
                request,
                template,
                {"form":
                    {'errors': "Need at least one numerical character in password."}})

        if email != email2:
            return render(
                request,
                template,
                {"form": {'errors': "Emails doesn't match."}})
        if password != password2:
            return render(
                request,
                template,
                {"form": {'errors': "Password doesn't match."}})

        if not password:
            return render(request, template, {"form": {'errors': "Need a valid password."}})

        if User.objects.filter(email=email).exists():
            return render(request, template, {"form": {'errors': "Email already used."}})

        try:
            user = User.objects.create_user(email, email, password)
            member = Member(user=user)
            member.save()
        except Exception:
            raise
            return render(request, template, {"form": {'errors': "Error while creating your account. Please contact me."}})

        return HttpResponse({'success': True, 'message': 'Account created!'})


class AccountView(TemplateView):
    def get(self, request):
        user = request.user
        member = Member.objects.get(user=user)
        package = Package.objects.filter(member=member)

        if package:
            package = package[0]

        return render(
            request,
            'account.html',
            {
                'package': package,
                'api_key': member.api_key,
                'email': user.email})


class GenerateAPIKey(View):
    http_method_names = ['get']

    def get(self, request):
        member = Member.objects.get(user=request.user)
        member.api_key = member.get_api_key()
        member.save()
        return HttpResponseRedirect(reverse('account'))
