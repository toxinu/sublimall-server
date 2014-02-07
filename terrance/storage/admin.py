# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Member
from .models import Package
from .models import Registration


class MemberInline(admin.TabularInline):
    model = Member
    can_delete = False


class UserAdmin(UserAdmin):
    inlines = (MemberInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Member)
admin.site.register(Package)
admin.site.register(Registration)
