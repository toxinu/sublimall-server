# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Donation


class DonationAdmin(admin.ModelAdmin):
    list_display = ('get_member', 'get_amount')
    raw_id_fields = ('member', )

    def get_amount(self, obj):
        return "%s $" % (obj.amount / 100)
    get_amount.short_description = "Amount"

    def get_member(self, obj):
        if obj.member:
            return obj.member.email
        return obj.email
    get_member.short_description = "Member"

admin.site.register(Donation, DonationAdmin)
