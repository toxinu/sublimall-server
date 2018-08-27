# -*- coding: utf-8 -*-
from django.conf import settings


def analytics(request):
    data = {}
    if hasattr(settings, "ANALYTICS_ENABLED"):
        data.update({"analytics_enabled": True})
    return data
