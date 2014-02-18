# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

from ..accounts.models import Member


class Package(models.Model):
    member = models.ForeignKey(Member)
    version = models.PositiveSmallIntegerField()
    platform = models.CharField(max_length=30, blank=True, null=True)
    arch = models.CharField(max_length=20, blank=True, null=True)
    update = models.DateTimeField(auto_now=True)
    package = models.FileField(upload_to=settings.PACKAGES_UPLOAD_TO)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.member.email

    @property
    def size(self):
        return self.package.file.size

    def clean(self):
        if self.package:
            if self.package.file.size > settings.MAX_PACKAGE_SIZE:
                raise ValidationError(
                    'Package size too big. Got %s (limit is %s).' % (
                        int(self.package.file.size / 1024 / 1024),
                        settings.MAX_PACKAGE_SIZE / 1024 / 1024))
        super(Package, self).clean()


@receiver(models.signals.post_delete, sender=Package)
def auto_delete_package_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `Package` object is deleted.
    """
    if default_storage.exists(instance.package.path):
        default_storage.delete(instance.package.path)


@receiver(models.signals.pre_save, sender=Package)
def auto_delete_package_on_change(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `Package` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_package = Package.objects.get(pk=instance.pk)
    except Package.DoesNotExist:
        return False

    if not default_storage.exists(old_package.package.path):
        return False

    new_package = instance.package.file
    if not old_package.package.file == new_package:
        default_storage.delete(old_package.package.path)
