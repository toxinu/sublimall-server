# -*- coding: utf-8 -*-
from __future__ import division
import stripe
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from ..accounts.models import Member

if hasattr(settings, "STRIPE_SECRET_KEY"):
    stripe.api_key = settings.STRIPE_SECRET_KEY


class Donation(models.Model):
    member = models.ForeignKey(Member, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    amount = models.IntegerField()
    token_id = models.CharField(max_length=50)
    charge_id = models.CharField(max_length=50, blank=True, null=True)
    paid = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def clean(self, *args, **kwargs):
        if not self.member and not self.email:
            raise ValidationError("Need an email or member")
        super(Donation, self).clean(*args, **kwargs)

    def get_email(self):
        if self.member:
            return self.member.email
        else:
            return self.email

    def get_formatted_amount(self):
        return self.amount / 100

    def charge(self):
        c = stripe.Charge.create(
            amount=self.amount,
            currency="eur",
            card=self.token_id,
            description="Charge for %s" % self.get_email(),
        )
        self.charge_id = c.id
        self.paid = c.paid
        self.save()

    def get_provider(self):
        if self.token_id.startswith("tok_"):
            return "Stripe"
        else:
            return "Paypal"

    def get_payment_url(self):
        if self.get_provider().lower() == "paypal":
            return "https://www.paypal.com/fr/vst/id=%s" % self.token_id
        else:
            return "https://manage.stripe.com/payments/%s" % self.charge_id
