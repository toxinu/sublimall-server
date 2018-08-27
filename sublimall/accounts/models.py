# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .utils import get_hash
from ..utils import send_custom_mail


class MemberManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), blank=True, unique=True)
    api_key = models.CharField(max_length=40, null=True, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    registration_key = models.CharField(
        max_length=40, default=get_hash, null=True, blank=True
    )
    password_key = models.CharField(max_length=40, null=True, blank=True)

    objects = MemberManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = get_hash()
        return super().save(*args, **kwargs)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def is_donator(self):
        if self.donation_set.filter(charge_id__isnull=False, paid=True).only("paid"):
            return True
        return False

    def get_storage_limit(self, is_donator=None):
        if is_donator is None:
            is_donator = self.is_donator()

        if is_donator:
            return settings.MAX_PACKAGE_SIZE_DONATE
        else:
            return settings.MAX_PACKAGE_SIZE

    def send_registration_confirmation(self, reset_key=False, connection=None):
        if reset_key:
            self.registration_key = get_hash()
            self.save()
        elif not self.registration_key:
            self.registration_key = get_hash()
            self.save()

        send_custom_mail(
            "Sublimall.org account creation confirmation",
            self.email,
            "registration",
            {
                "registration_link": urljoin(
                    settings.SITE_URL,
                    reverse(
                        "registration-confirmation",
                        args=[self.id, self.registration_key],
                    ),
                )
            },
            connection=connection,
        )
