# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError

from ..accounts.models import Member


class Package(models.Model):
    member = models.ForeignKey(Member)
    version = models.PositiveSmallIntegerField()
    platform = models.CharField(max_length=30, blank=True, null=True)
    arch = models.CharField(max_length=20, blank=True, null=True)
    update = models.DateTimeField(auto_now=True)
    package = models.FileField(upload_to='packages')

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s" % self.member.user.email

    def clean(self):
        if self.package.file.size > 20 * 1024 * 1024:
            raise ValidationError(
                'Package size too big. Got %s (limit is %s).' % (
                    int(self.package.file.size / 1024 / 1024), 20))
        super(Package, self).clean()

    def delete(self, *args, **kwargs):
        storage, path = self.package.storage, self.package.path
        super(Package, self).delete(*args, **kwargs)
        storage.delete(path)
