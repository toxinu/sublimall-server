# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .utils import get_hash


class Member(models.Model):
    user = models.OneToOneField(User)
    api_key = models.CharField(max_length=40)

    def __unicode__(self):
        return self.user.email

    def get_api_key(self):
        return get_hash()

    def save(self):
        if not self.api_key:
            self.api_key = self.get_api_key()
        return super(Member, self).save()


class Registration(models.Model):
    member = models.OneToOneField(Member)
    key = models.CharField(max_length=40)


class Package(models.Model):
    member = models.ForeignKey(Member)
    version = models.CharField(max_length=20)
    update = models.DateTimeField(auto_now=True)
    package = models.FileField(upload_to='packages')

    def clean(self):
        if self.package.file.size > 20 * 1024:
            raise ValidationError('Package size too big.')
        super(Package, self).clean()
