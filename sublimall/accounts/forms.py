# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password."),
        'inactive': _("This account is inactive."),
    }
