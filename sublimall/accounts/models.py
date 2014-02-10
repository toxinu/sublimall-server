# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _


from .utils import get_hash


# class MemberManager(BaseUserManager):
#     def _create_user(self, email, password,
#                      is_staff, is_superuser, **extra_fields):
#         """
#         Creates and saves a User with the given email and password.
#         """
#         now = timezone.now()
#         if not email:
#             raise ValueError('The given email must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email,
#                           is_staff=is_staff, is_active=True,
#                           is_superuser=is_superuser, last_login=now,
#                           date_joined=now, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_user(self, email=None, password=None, **extra_fields):
#         return self._create_user(email, password, False, False,
#                                  **extra_fields)

#     def create_superuser(self, email, password, **extra_fields):
#         return self._create_user(email, password, True, True,
#                                  **extra_fields)


# class Member(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(_('email address'), blank=True, unique=True)
#     api_key = models.CharField(max_length=40, null=True, blank=True)
#     is_staff = models.BooleanField(
#         _('staff status'),
#         default=False,
#         help_text=_('Designates whether the user can log into this admin site.'))
#     date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

#     objects = UserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def save(self):
#         if not self.api_key:
#             self.api_key = get_hash()
#         return super(Member, self).save()


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
