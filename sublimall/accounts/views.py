# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from .models import Member
from .models import Registration
from ..storage.models import Package

from .utils import get_hash

logger = logging.getLogger(__name__)


class MaintenanceView(TemplateView):
    template_name = "error.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Sublimall is in maintenance'
        context['error'] = '<p>Sorry, Sublimall is under maintenance.</p>' \
            '<p>Try again a little later.</p><p>Socketubs.</p>'
        context['hide_navbar'] = True
        return context


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        data = {
            'data': {},
            'files': kwargs.get('files'),
            'initial': kwargs.get('initial'),
            'prefix': kwargs.get('prefix')}

        if self.request.method == 'POST' and kwargs.get('data'):
            for field in ['next', 'username', 'csrfmiddlewaretoken', 'password']:
                data['data'][field] = kwargs['data'].get(field)
            data['data']['username'] = data['data']['username'].lower()
        else:
            data = kwargs

        return form_class(**data)

    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account'))
        return super(LoginView, self).get(request)

    def form_valid(self, form):
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
        current_user_count = Member.objects.all().count()
        if current_user_count >= settings.MAX_MEMBER:
            msg = "I'm sorry about that, don't forget that it's " \
                "a beta version of Sublimall. <br /><strong>Registrations will " \
                "been soon re-opened!</strong></p><p><em>Geoffrey.</em>"
            return render(
                request, 'error.html', {'title': 'Max registration reach', 'error': msg})
        return render(request, 'registration.html')

    @transaction.commit_on_success
    def post(self, request):
        template = 'registration.html'

        current_user_count = Member.objects.all().count()
        if current_user_count >= settings.MAX_MEMBER:
            logger.warn('Max registration number reached')
            return render(
                request,
                template,
                {'form':
                    {'errors':
                        "Max member reach. I'm sorry about that, "
                        "don't forget that it's a beta version of Sublimall. "
                        "Registrations will been soon re-opened!"}})

        email = request.POST.get('email')
        email2 = request.POST.get('email2')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not email:
            return render(
                request, template, {"form": {'errors': "Email can't be empty."}})
        if not password:
            return render(
                request, template, {"form": {'errors': "Password can't be empty."}})

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

        if Member.objects.filter(email=email).exists():
            return render(request, template, {"form": {'errors': "Email already used."}})

        try:
            member = Member(email=email, is_active=False)
            member.set_password(password)
            member.full_clean()
            member.save()

            registration = Registration(member=member, key=get_hash())
            registration.full_clean()
            registration.save()

            send_mail(
                'Sublimall registration confirmation',
                'Welcome on Sublimall!\nClick here to validate your account:\n'
                '%s\n\n'
                "Let's go to documentation to learn how to install SublimeText plugin.\n"
                "%s\nBye!" % (
                    urljoin(
                        settings.SITE_URL,
                        reverse(
                            'registration-confirmation',
                            args=[registration.id, registration.key])),
                    urljoin(settings.SITE_URL, reverse('docs'))),
                settings.FROM_EMAIL,
                [email])
        except Exception:
            logger.error(
                'Registration unhandled exception',
                exc_info=True,
                extra={'request': request})
            return render(
                request,
                template,
                {"form": {
                    'errors':
                    "Error while creating your account. "
                    "A report have been sent. Sorry about that."}})

        messages.success(
            request,
            "You'll received an email soon, check it to confirm "
            "your account. See you soon!")
        return HttpResponseRedirect(reverse('login'))


class RegistrationConfirmationView(View):
    http_method_names = ['get']

    def get(self, request, **kwargs):
        key = kwargs.get('key')
        pk = kwargs.get('pk')

        try:
            registration = Registration.objects.get(pk=pk)
        except Registration.DoesNotExist:
            registration = None

        if registration is None:
            return render(
                request, 'error.html', {'title': 'Error', 'error': 'Invalid key.'})
        if key != registration.key:
            return render(
                request, 'error.html', {'title': 'Error', 'error': 'Invalid key.'})

        member = registration.member
        member.is_active = True
        member.save()

        registration.delete()

        return HttpResponseRedirect(reverse('login'))


class AccountView(TemplateView):
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        member = request.user
        packages = Package.objects.filter(member=member)

        return render(
            request,
            'account.html',
            {
                'packages': packages,
                'api_key': member.api_key,
                'email': member.email})


class GenerateAPIKey(View):
    http_method_names = ['get']

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        member = request.user
        member.api_key = get_hash()
        member.save()
        return HttpResponseRedirect(reverse('account'))
