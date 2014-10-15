# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'get_display_title', 'added', 'member', 'level', 'is_draft', )
    list_filter = ('is_draft', 'level', )
    raw_id_fields = ('member', )

    def get_display_title(self, obj):
        if len(obj.title) > 30:
            return obj.title[:-4] + ' ...'
        return obj.title
    get_display_title.short_description = 'Title'

admin.site.register(Notification, NotificationAdmin)
