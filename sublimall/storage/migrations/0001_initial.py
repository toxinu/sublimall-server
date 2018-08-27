# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Package",
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
                ("version", models.PositiveSmallIntegerField()),
                ("platform", models.CharField(max_length=30, null=True, blank=True)),
                ("arch", models.CharField(max_length=20, null=True, blank=True)),
                ("update", models.DateTimeField(auto_now=True)),
                ("package", models.FileField(upload_to="packages")),
                ("member", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={},
            bases=(models.Model,),
        )
    ]
