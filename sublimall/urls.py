# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.views.generic import TemplateView

from .donations.views import DonationsView

from .storage.views import DeletePackageView
from .storage.views import DeletePackageAPIView
from .storage.views import UploadPackageAPIView
from .storage.views import MaxPackageSizeAPIView
from .storage.views import DownloadPackageAPIView

from .accounts.views import LoginView
from .accounts.views import LogoutView
from .accounts.views import AccountView
from .accounts.views import GenerateAPIKey
from .accounts.views import MaintenanceView
from .accounts.views import RegistrationView
from .accounts.views import AccountDeleteView
from .accounts.views import PasswordRecoveryView
from .accounts.views import ResendRegistrationView
from .accounts.views import RegistrationConfirmationView
from .accounts.views import PasswordRecoveryConfirmationView

admin.autodiscover()

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    # url(r'^', MaintenanceView.as_view(), name='maintenance'),
    url(r"^api/upload/$", UploadPackageAPIView.as_view(), name="api-upload"),
    url(r"^api/retrieve/$", DownloadPackageAPIView.as_view(), name="api-download"),
    url(r"^api/delete/$", DeletePackageAPIView.as_view(), name="api-delete"),
    url(
        r"^api/max-package-size/$",
        MaxPackageSizeAPIView.as_view(),
        name="api-max-package-size",
    ),
    url(
        r"^delete/package/(?P<pk>\d+)/$",
        DeletePackageView.as_view(),
        name="delete-package",
    ),
    url(r"^$", TemplateView.as_view(template_name="home.html"), name="home"),
    url(r"^login/$", LoginView.as_view(), name="login"),
    url(r"^logout/$", LogoutView.as_view(), name="logout"),
    url(
        r"^login/password-recovery$",
        PasswordRecoveryView.as_view(),
        name="password-recovery",
    ),
    url(
        r"^login/password-recovery/(?P<pk>\d+)/(?P<key>[\w{}.-]{1,40})$",
        PasswordRecoveryConfirmationView.as_view(),
        name="password-recovery-confirmation",
    ),
    url(r"^registration/$", RegistrationView.as_view(), name="registration"),
    url(
        r"^registration/resend$",
        ResendRegistrationView.as_view(),
        name="registration-resend",
    ),
    url(
        r"^registration/(?P<pk>\d+)/(?P<key>[\w{}.-]{1,40})$",
        RegistrationConfirmationView.as_view(),
        name="registration-confirmation",
    ),
    url(r"^account/$", AccountView.as_view(), name="account"),
    url(r"^account/delete$", AccountDeleteView.as_view(), name="account-delete"),
    url(r"^account/new_api_key$", GenerateAPIKey.as_view(), name="account-new-api-key"),
    url(r"^docs$", TemplateView.as_view(template_name="docs.html"), name="docs"),
    url(r"^donate$", DonationsView.as_view(), name="donations"),
]
