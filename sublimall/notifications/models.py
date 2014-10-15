# -*- coding: utf-8 -*-
from django.db import models

from ..accounts.models import Member


class Notification(models.Model):
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    DANGER = 'danger'
    DEFAULT_LEVEL = INFO
    LEVEL_CHOICES = (
        (SUCCESS, 'Success'),
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (DANGER, 'Danger'),
    )
    member = models.ForeignKey(Member)
    added = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=50)
    short_text = models.TextField(max_length=300)
    text = models.TextField(blank=True, null=True)
    level = models.CharField(
        max_length=10, choices=LEVEL_CHOICES, default=DEFAULT_LEVEL)
    is_draft = models.BooleanField(default=True)
