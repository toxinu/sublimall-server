# -*- coding: utf-8 -*-
import random
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Member(models.Model):
    user = models.OneToOneField(User)
    api_key = models.CharField(max_length=100)

    def __unicode__(self):
        return self.user.email

    def get_api_key(self):
        return hashlib.sha224(
            str(random.getrandbits(256)).encode('utf-8')).hexdigest()[:40]

    def save(self):
        if not self.api_key:
            self.api_key = self.get_api_key()
        return super(Member, self).save()


class Package(models.Model):
    member = models.ForeignKey(Member)
    version = models.CharField(max_length=20)
    update = models.DateTimeField(auto_now=True)
    package = models.FileField(upload_to='packages')

    def clean(self):
        if self.package.file.size > 20 * 1024:
            raise ValidationError('Package size too big.')
        super(Package, self).clean()
