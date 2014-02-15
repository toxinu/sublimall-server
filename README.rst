Sublimall
=========

.. image:: https://magnum.travis-ci.com/socketubs/sublimall-server.png?token=8Rz7PXRsaTFUz7F3LJzS&branch=master
    :target: https://magnum.travis-ci.com/socketubs/sublimall-server

Sublimall is Python 3.3 server behind Sublimall SublimeText plugin.


Installation
~~~~~~~~~~~~

::

    git clone https://github.com/socketubs/sublimall-server.git
    cd sublimall-server
    virtualenv-3.3 virtenv
    source virtenv
    pip install -r requirements.txt
    python manage.py syncdb
    python manage.py runserver


Tests
~~~~~

Sublimall server is tested at ~90% coverage.

::

    pip install coverage
    make coverage
    firefox htmlcov/index.html
