# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Member
from .models import Registration


class MemberInline(admin.TabularInline):
    model = Member
    can_delete = False


class MemberAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'api_key', )

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'key', )

    def get_email(self, obj):
        return obj.member.user.email
    get_email.short_description = 'Email'


class UserAdmin(UserAdmin):
    inlines = (MemberInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Registration, RegistrationAdmin)
