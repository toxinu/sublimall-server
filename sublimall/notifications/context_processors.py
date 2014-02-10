# -*- coding: utf-8 -*-
from .models import Notification


def notifications(request):
    data = {}
    if request.user.is_authenticated():
        notifications = Notification.objects.filter(is_draft=False).order_by(
            '-added').only('level', 'title', 'short_text', 'added')[:2]
        data.update({'notifications': notifications})
    return data
