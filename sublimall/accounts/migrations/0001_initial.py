# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import sublimall.accounts.utils


class Migration(migrations.Migration):

    dependencies = [("auth", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        verbose_name="superuser status",
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=75,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                ("api_key", models.CharField(blank=True, null=True, max_length=40)),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        verbose_name="staff status",
                        help_text="Designates whether the user can log into this admin site.",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=False,
                        verbose_name="active",
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "registration_key",
                    models.CharField(
                        blank=True,
                        null=True,
                        default=sublimall.accounts.utils.get_hash,
                        max_length=40,
                    ),
                ),
                (
                    "password_key",
                    models.CharField(blank=True, null=True, max_length=40),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        to="auth.Group",
                        related_name="user_set",
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of his/her group.",
                        verbose_name="groups",
                        related_query_name="user",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        to="auth.Permission",
                        related_name="user_set",
                        blank=True,
                        help_text="Specific permissions for this user.",
                        verbose_name="user permissions",
                        related_query_name="user",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        )
    ]
