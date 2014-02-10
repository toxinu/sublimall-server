# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'api_key', 'is_active', 'date_joined', 'last_login', 'is_staff', )
    list_filter = ('is_staff', 'date_joined', 'last_login', )
    search_fields = ('id', 'email', )

admin.site.register(Member, MemberAdmin)
