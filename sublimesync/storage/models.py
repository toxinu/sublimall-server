# -*- coding: utf-8 -*-
import random
import hashlib
from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
	user = models.OneToOneField(User)
	api_key = models.CharField(max_length=100)

	def get_api_key(self):
		return hashlib.sha224( str(random.getrandbits(256)) ).hexdigest()[:40]

	def clean(self):
		if not self.api_key:
			self.api_key = self.get_api_key()
		return super(Member, self).clean()
		

class Package(models.Model):
	member = models.ForeignKey(Member)
	version = models.CharField(max_length=10)
	update = models.DateTimeField(auto_now=True)
	package = models.FileField(upload_to='packages')
