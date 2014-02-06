Terrance
========

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
