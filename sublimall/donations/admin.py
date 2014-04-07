# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Donation


class DonationAdmin(admin.ModelAdmin):
    list_display = ('get_member', 'get_amount', 'get_provider', 'get_payment_url')
    search_fields = ('id', 'member__email', 'email')
    raw_id_fields = ('member', )

    def get_amount(self, obj):
        return "%s $" % (obj.amount / 100)
    get_amount.short_description = "Amount"

    def get_member(self, obj):
        if obj.member:
            return obj.member.email
        return obj.email
    get_member.short_description = "Member"

    def get_provider(self, obj):
        return obj.get_provider()
    get_provider.short_description = "Provider"

    def get_payment_url(self, obj):
        return '<a href="%s">Link</a>' % obj.get_payment_url()
    get_payment_url.allow_tags = True
    get_payment_url.short_description = "Link"

admin.site.register(Donation, DonationAdmin)
