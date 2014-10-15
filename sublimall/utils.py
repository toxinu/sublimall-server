# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_custom_mail(subject, to, template, context, connection=None):
    context.update({'SITE_URL': settings.SITE_URL})
    text_content = render_to_string('email/%s.txt' % template, context)
    html_content = render_to_string('email/%s.html' % template, context)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.FROM_EMAIL,
        [to],
        connection=connection)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
