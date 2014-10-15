# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.mail import get_connection

from .models import Member
from ..storage.models import Package


class PackageInline(admin.TabularInline):
    model = Package
    max_num = 1


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'api_key', 'is_active', 'date_joined',
        'last_login', 'is_staff', )
    list_filter = ('is_active', 'is_staff', 'date_joined', 'last_login', )
    search_fields = ('id', 'email', )
    actions = ['resend_registration']
    actions_on_bottom = True
    exclude = ('groups', 'user_permissions', )
    inlines = [PackageInline, ]

    def resend_registration(self, request, queryset):
        connection = get_connection()
        for member in queryset.all().only('registration_key', 'email', 'id'):
            member.send_registration_confirmation(
                reset_key=True, connection=connection)

admin.site.register(Member, MemberAdmin)
