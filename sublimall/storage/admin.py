# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Package


class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'member', 'version', 'platform', 'arch',
        'get_display_size', 'update', )
    list_filter = ('version', 'platform', 'arch', 'update', )
    search_fields = ('id', 'member__email', )

    def get_display_size(self, obj):
        return "%.2f MB" % (obj.size / 1024 / 1024)
    get_display_size.short_description = 'Size'

admin.site.register(Package, PackageAdmin)
