# Set up you own Sublimall server

## Requirements

You'll need:
 - Python 3
 - Database like Postgresql is optionnal if you use Sublimall for personnal or few users
 
## Installation

```
cd /var/www
git clone https://github.com/socketubs/sublimall-server.git sublimall
cd sublimall
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
cp sublimall/local_settings_example.py sublimall/local_settings.py
./manage.py migrate
./manage.py createsuperuser
pip install gunicorn
```

## Deployment

I recommend using whatever software you are most familiar with for managing Sublimall process. For me, that software of choice is [Supervisor][0].
Configuring Supervisor couldn’t be more simple. Just point it to the sentry executable in your virtualenv’s bin/ folder and you’re good to go.

If you want to use only for you or small team you can change `MAX_MEMBER` in your `local_settings.py` file.

```
[program:sublimall]
directory=/var/www/sublimall
command=/var/www/sublimall/venv/bin/gunicorn sublimall.wsgi:application --log-file=-
autostart=true
autorestart=true
redirect_stderr=true
```

## Plugin

And you just have to change your Sublime Text plugin settings.

```
"api_root_url": "http://<ip>:<port>",
```

[0]: http://supervisord.org/
