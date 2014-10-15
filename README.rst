Sublimall
=========

.. image:: https://coveralls.io/repos/socketubs/sublimall-server/badge.png
  :target: https://coveralls.io/r/socketubs/sublimall-server

.. image:: https://badges.gitter.im/socketubs/Sublimall.png
  :target: https://gitter.im/socketubs/Sublimall

Sublimall is Python 3 server behind Sublimall_ SublimeText plugin.

Installation
~~~~~~~~~~~~

::

    git clone https://github.com/socketubs/sublimall-server.git
    cd sublimall-server
    virtualenv-3 virtenv
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

.. _Sublimall: https://github.com/socketubs/Sublimall
