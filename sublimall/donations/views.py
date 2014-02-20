# -*- coding: utf-8 -*-
import json
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest

from .models import Donation

from sublimall.mixins import APIMixin


class DonationsView(APIMixin, View):
    http_method_names = ['post', 'get']

    def get(self, request):
        context = {}
        if request.user.is_authenticated():
            context.update({'email': request.user.email})
        context.update({'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})
        return render(request, 'donations.html', context)

    def post(self, request):
        email = request.POST.get('email')
        token = request.POST.get('token')
        amount = request.POST.get('amount')

        if not email or not token or not amount:
            message = {'success': False, 'errors': []}
            messages.error(request, "Failed to proceed donation, sorry about that.")
            if not email:
                message['errors'].append('Email is mandatory')
            if not token:
                message['errors'].append('Token is mandatory')
            if not amount:
                message['errors'].append('Amount is mandatory')
            return HttpResponseBadRequest(json.dumps(message))

        if request.user.is_authenticated():
            donation = Donation(member=request.user, token_id=token, amount=amount)
        else:
            donation = Donation(email=email, token_id=token, amount=amount)

        try:
            donation.full_clean()
            donation.charge()
            if not donation.paid:
                raise Exception
        except:
            messages.error(request, "Failed to proceed donation, sorry about that.")
            return HttpResponse(json.dumps(
                {'success': False, 'error': 'Failed to credit your card.'}))

        donation.save()
        messages.success(
            request, "Thank you for your donation.<br />Your account is now upgrade!")
        return HttpResponse(json.dumps({'success': True, 'amount': amount}))
