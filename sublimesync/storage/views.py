# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest

from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from .utils import get_hash

from .models import Member
from .models import Package
from .models import Registration
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


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account'))
        return super(LoginView, self).get(request)

    def form_valid(self, form):
        # Don't login if not active
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return HttpResponseRedirect(reverse('account'))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class RegistrationView(View):
    http_method_names = ['get', 'post']

    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account'))
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
            user.is_active = False
            member = Member(user=user)
            member.save()

            registration = Registration(member=member, key=get_hash())
            registration.save()

            send_mail(
                'Sublime Sync registration confirmation',
                'Welcome on Sublime Sync!\nClick here to validate your account:\n'
                '%s' % reverse('registration-confirmation', args=[registration.key]),
                'norepply@sublimesync',
                [email])
        except Exception:
            raise
            return render(
                request,
                template,
                {"form": {'errors': "Error while creating your account. Please contact me."}})

        return HttpResponseRedirect(reverse('login'))


class RegistrationConfirmationView(View):
    http_method_names = ['get']

    def get(self, request):
        print(request)


class AccountView(TemplateView):
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

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
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        member = Member.objects.get(user=request.user)
        member.api_key = get_hash()
        member.save()
        return HttpResponseRedirect(reverse('account'))
