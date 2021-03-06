# Deployment instructions

voltairine is a regular Django project, apart from the dependencies for pyav, nothing
is a special case, so this will basically describe a traditional python/Django
deployment instruction for nginx/supervisord/git/virtualenv/Django.

This tutorial assume that you are using the **last debian stable**.

## Create a new user

In root:

    adduser voltairine
    # fill blank informations and no password

## Configure the database

We'll use postgresql.

    apt-get install postgresql
    su postgres
    createuser voltairine  # if ask, don't set the user as a superuser, it's better for security
    createdb -O voltairine voltairine  # create a dabatase for this user
    exit

## Get ffmpeg

You need some pkgs first:

    apt-get install yasm pkg-config

Follow [those instructions](https://mikeboers.github.io/PyAV/#ubuntu-12-04-lts)
and do a <code>ldconfig</code> at the end.

Don't forget that you can add <code>-j $NUMBER</code> (where
<code>$NUMBER</code> is generally the number of core that you have) to speed up
the compilation.

## Get the code

    apt-get install git python-virtualenv python-dev

    su voltairine
    cd  # will get you into his home
    git clone https://github.com/psycojoker/voltairine

## Install dependencies

    cd voltairine

    # dependancies installation
    virtualenv ve

    # THIS IS A VERY IMPORTANT LINE: this basically "chroot" your current "python" command to inside the virtualenv
    # ALWAYS make sure that you are launching python command with the virtualenv activated
    # other you'll have missing dependancies bugs
    source ve/bin/activate

    pip install -r requirements.txt

    pip install gunicorn  # production wsgi server

    pip install psycopg2  # for postgresql, you might need to install the debian pkg for postgresql headers (the one with "-dev" in it)
## Add the production configuration

Create the file `/home/voltairine/voltairine/voltairine/settings_local.py` and **adapt** the
following content for it:

```python
SECRET_KEY = 'put something random very long here'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['my.domain.name']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'voltairine',
    }
}

# this is where the static assets will be store (for example "jquery.min.js" or css files)
STATIC_ROOT = '/home/voltairine/voltairine/static_deploy/static/'

# this is where the videos will be stored
MEDIA_ROOT = '/home/voltairine/voltairine/media_deploy/media/'

SAYA_FORGOTTEN_PASSWORD_EMAILS = ['email']
```


## Configure the database

    python manage.py syncdb  # create a superuser when ask

    # if you failed to create a super user you can run:
    # python manage.py createsuperuser
    python manage.py makemigrations

    # yes, again
    python manage.py syncdb

## A first test of the installation

    python manage.py runserver

If it runs without any error, it's a good sign. You can look at
<code>http://localhost:8000</code> to a play a bit with it if you want (with
curl or something like that). You can also run it this way to access if from
outside the server on which it is running (or change the port):

    python manage.py runserver 0.0.0.0:8000

**Never run this setup in production**.

## Collect the static

Django doesn't serve static files, so it puts them all in one directory that
we'll give to nginx.

    python manage.py collecstatic

Answer "yes".

## Setup nginx

If nginx isn't already installed:

    apt-get install nginx

Then, put **adapt** this content and put it into the file
<code>/etc/nginx/sites-available/voltairine</code>:

```
server {
    listen 80;
    server_name my.domain.name;
    access_log  /var/log/nginx/voltairine_access.log;
    error_log   /var/log/nginx/voltairine_error.log;

    client_max_body_size 500M;

    location /administration/video/ {
        add_header Access-Control-Allow-Origin *;
        proxy_pass        http://localhost:8000;
        proxy_set_header  X-Real-IP  $remote_addr;
    }

    location / {
        proxy_pass        http://localhost:8000;  # you might want to change the port number if it's already used
        proxy_set_header  X-Real-IP  $remote_addr;
        proxy_set_header Host $host;
    }

    location /static/  {
        autoindex    off;
        root /home/voltairine/voltairine/static_deploy/;
    }

    location /media/  {
        autoindex    off;
        root /home/voltairine/voltairine/media_prod/;
    }
}
```

**If you have changed the static/media paths in the
<code>settings_local.py</code> you'll have to change it here too.**

Symlink this file in the good place:

    ln -s /etc/nginx/sites-available/voltairine /etc/nginx/sites-enabled/voltairine

Reload nginx:

    nginx reload

This is not working yet, so if you go to "my.domain.name" you'll have a "bad gateway error" for now.

## Test the deployment again

Run this (adapt port if needed):

    /home/voltairine/voltairine/ve/bin/gunicorn voltairine.wsgi:application -b localhost:8000 --workers=1

Then go to <code>my.domain.name</code>. It should be working.

Some common errors:

* error 400: you haven't configured <code>ALLOWED_HOSTS</code> correctly
* no css/javascript: either missing <code>collecstatic</code> command or bad path in <code>settings_local.py</code> or nginx config file
* error 500: huho, that's bad, change <code>DEBUG = False</code> to <code>DEBUG = True</code> in `settings_local.py`, runlaunch gunicorn, then look at the error (**never run with this configuration in production**), then once it's finished, switch DEBUG back to <code>False</code>.

Hopefully, by now, everything is fine, **stop** gunicorn then proceed.

## Use supervisord to avoid using a screen

    apt-get install supervisor

Then adapt this config file and put it here <code>/etc/supervisor/conf.d/voltairine.conf</code>:

```
[program:voltairine]
command=/home/voltairine/voltairine/ve/bin/gunicorn voltairine.wsgi:application -b localhost:8000 --workers=4 
stdout_logfile=/var/log/voltairine.log
stderr_logfile=/var/log/voltairine.err.log
directory=/data/voltairine
user=voltairine
```

Then run:

    supervisorctl update

And now, everything should be running fine, hopefully. If you have an error, look at the previous common error or launch this command to have a bit of informations:

    supervisorctl status

Now, remember, **every time** you modify your python code, you **have** to do restart the daemon using:

    supervisorctl restart voltairine

Common supervisorctl commands:

* start <projects names>
* stop <projects names>
* restart <projects names>
* update  # you have to do this every time you modify a <code>/etc/supervisor/conf.d/*.conf</code> file.
* status

You can replace supervisorctl with an init or systemd script if you want.
