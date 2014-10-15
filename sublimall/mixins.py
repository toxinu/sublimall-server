# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from .accounts.models import Member


class APIMixin(object):
    http_method_names = ['post']

    def get_member(self, email, api_key):
        try:
            return Member.objects.get(email=email, api_key=api_key)
        except Member.DoesNotExist:
            return None

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)
