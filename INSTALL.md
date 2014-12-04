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
virtualenv -p /usr/bin/python3 venv
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

For nginx, this is a production server configuration file dump:

```
server {
    listen 80;
    server_name example.com;

    error_log /var/log/nginx/sublimall.error.log;
    access_log /var/log/nginx/sublimall.access.log;

    client_max_body_size 150m;

    location /api {
        proxy_hide_header Server;

        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Ssl on;
        proxy_pass http://127.0.0.1:9002;
    }

    location / {
        rewrite ^ https://example.com$request_uri permanent;
    }
}
server {
    listen 443 ssl spdy;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/sublimall.public.crt;
    ssl_certificate_key /etc/nginx/ssl/sublimall.private.rsa;
    
    error_log /var/log/nginx/sublimall.error.log;
    access_log /var/log/nginx/sublimall.access.log;

    if ($http_host != "sublimall.org") {
        rewrite ^ https://example.com$request_uri permanent;
    }

    location /api {
        rewrite ^ http://example.com$request_uri permanent;
    }

    location /static {
        autoindex on;
        root /var/www/sublimall;
    }

    location / {
        proxy_hide_header Server;

        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Ssl on;
        proxy_pass http://127.0.0.1:9002;
    }
}
```

As you can see, configuration file include ssl, which you can drop easily.

## Plugin

And you just have to change your Sublime Text plugin settings.

```
"api_root_url": "http://<ip>:<port>",
```

[0]: http://supervisord.org/
