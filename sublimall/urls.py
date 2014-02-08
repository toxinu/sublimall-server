# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy

from .storage.views import UploadPackageAPIView
from .storage.views import DownloadPackageAPIView

from .accounts.views import LoginView
from .accounts.views import AccountView
from .accounts.views import GenerateAPIKey
from .accounts.views import RegistrationView
from .accounts.views import RegistrationConfirmationView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/upload/$', UploadPackageAPIView.as_view(), name='api-upload'),
    url(r'^api/retrieve/$', DownloadPackageAPIView.as_view(), name='api-download'),
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': reverse_lazy('home')}, name='logout'),
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),
    url(r'^registration/(?P<pk>\d+)/(?P<key>[\w{}.-]{1,40})$', RegistrationConfirmationView.as_view(), name='registration-confirmation'),
    url(r'^account/$', AccountView.as_view(), name='account'),
    url(r'^account/new_api_key$', GenerateAPIKey.as_view(), name='account-new-api-key'),
    url(r'^docs$', TemplateView.as_view(template_name="docs.html"), name='docs'),
)
