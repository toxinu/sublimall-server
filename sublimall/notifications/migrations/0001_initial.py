# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                        primary_key=True,
                    ),
                ),
                ("added", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=50)),
                ("short_text", models.TextField(max_length=300)),
                ("text", models.TextField(null=True, blank=True)),
                (
                    "level",
                    models.CharField(
                        max_length=10,
                        default="info",
                        choices=[
                            ("success", "Success"),
                            ("info", "Info"),
                            ("warning", "Warning"),
                            ("danger", "Danger"),
                        ],
                    ),
                ),
                ("is_draft", models.BooleanField(default=True)),
                ("member", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={},
            bases=(models.Model,),
        )
    ]
