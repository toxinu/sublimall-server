# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from .utils import get_hash


class Member(models.Model):
    user = models.OneToOneField(User)
    api_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.user.email

    def save(self):
        if not self.api_key:
            self.api_key = get_hash()
        return super(Member, self).save()


class Registration(models.Model):
    member = models.OneToOneField(Member)
    key = models.CharField(max_length=40)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s (%s)" % (self.member.user.email, self.key)

    def save(self):
        if not self.key:
            self.key = get_hash()
        return super(Registration, self).save()
