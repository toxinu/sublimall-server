Sublimall
=========

.. image:: https://coveralls.io/repos/socketubs/sublimall-server/badge.png
  :target: https://coveralls.io/r/socketubs/sublimall-server

Sublimall is Python 3.6 server behind Sublimall_ SublimeText plugin.

Installation
~~~~~~~~~~~~

Let's read INSTALL.md or follow this quick and dirty install steps:

::

    git clone https://github.com/socketubs/sublimall-server.git
    cd sublimall-server
    virtualenv virtenv
    source virtenv
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Tests
~~~~~

Sublimall server is tested at ~90% coverage.

::

    pip install coverage
    make coverage
    firefox htmlcov/index.html

.. _Sublimall: https://github.com/socketubs/Sublimall
