Sublimall
=========

.. image:: https://travis-ci.org/toxinu/sublimall-server.svg?branch=master
  :target: https://travis-ci.org/toxinu/sublimall-server
.. image:: https://coveralls.io/repos/github/toxinu/sublimall-server/badge.svg?branch=master
  :target: https://coveralls.io/github/toxinu/sublimall-server?branch=master

Sublimall is Python 3.6 server behind Sublimall_ SublimeText plugin.

Installation
~~~~~~~~~~~~

Let's read INSTALL.md or follow this quick and dirty install steps:

::

    git clone https://github.com/toxinu/sublimall-server.git
    cd sublimall-server
    virtualenv virtenv
    source virtenv/bin/activate
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

.. _Sublimall: https://github.com/toxinu/sublimall
