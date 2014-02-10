# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Member
from .models import Registration


class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'api_key', 'is_active', )


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'key', )

    def get_email(self, obj):
        return obj.member.email
    get_email.short_description = 'Email'


admin.site.register(Member, MemberAdmin)
admin.site.register(Registration, RegistrationAdmin)
