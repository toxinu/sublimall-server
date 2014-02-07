Terrance
========

.. image:: https://magnum.travis-ci.com/socketubs/terrance-server.png?token=8Rz7PXRsaTFUz7F3LJzS&branch=master
    :target: https://magnum.travis-ci.com/socketubs/terrance-server

Terrance is server behind Terrance SublimeText plugin.


Installation
~~~~~~~~~~~~

::

    git clone https://github.com/socketubs/terrance-server.git
    cd terrance-server
    virtualenv-3.3 virtenv
    source virtenv
    pip install -r requirements.txt
    python manage.py syncdb
    python manage.py runserver


Tests
~~~~~

Terrance server is tested at ~90% coverage.

::
    pip install coverage
    make coverage
    firefox htmlcov/index.html
