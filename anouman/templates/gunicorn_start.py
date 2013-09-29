#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put in a few files to make sure it was called...
try: settings.configure()
except: pass

"""
    Render the gunicorn_start.py command file.

    gunicorn_start.py is a custom configued gunicorn script
    based on your django projec.
"""


# These are the context variables used to render the gunicorn_start.sh from
# The templ string is found below
context = {
    'NAME':'website',                           # Name of the application
    'DJANGODIR':'./',                           # Django project director
    'USER':'username',                          # user to run as
    'GROUP':'username',                         # group to run as
    'NUM_WORKERS':3,                            # Number of Gunicorn threads.  2(proc)+1
    'VIRTUALENVDIR':'./virtualenv',             # Directory containing your projects virtual env
    'DJANGO_SETTINGS_MODULE':'website.settings',# the django settings file
    'DJANGO_WSGI_MODULE':'website.wsgi',        # your project wsgi module
    'GUNICORN':'virtualenv/bin/gunicorn',       # location of gunicorn.py

    #   You can bind your server to a unix socket or to a port
    #   But you should only bind it to one or the other
    #   unix socket example: /var/run/gunicorn.sock
    #   ip:port example:    10.0.2.13:8000
    'BIND':False,                      # ex:  10.0.2.13:80
    'SOCKFILE':False,                   # ex:  /var/run/gunicorn.sock
}



# This is the template used to generate the gunicorn_start.sh command
templ="""#!/bin/bash

# Export your projects settings module

export DJANGO_SETTINGS_MODULE={{DJANGO_SETTINGS_MODULE}}

# Make sure your project is at the beginning of PYTHONPATH
export PYTHONPATH={{DJANGODIR}}:$PYTHONPATH

# Create the run directory if it doesn't exist
{% if SOCKFILE %}
RUNDIR=$(dirname {{SOCKFILE}})
test -d $RUNDIR || mkdir -p $RUNDIR
{% endif %}

# Start gunicorn
exec {{GUNICORN}} {{DJANGO_WSGI_MODULE}}:application \
  --bind={{BIND}} \
  --name {{NAME}} \
  --workers {{NUM_WORKERS}} \
  --user={{USER}} \
  --log-level=debug  \
  {% if DAEMON %} --daemon \{% endif %}

echo "gunicorn start for site: {{NAME}}"
"""

def render(c={}):
    """
        Pass in a context our the defaults above will be used
    """ 
    context.update(c)

    t = Template( templ )
    c = Context( context )
    return t.render( c )

def save(path="./gunicorn_start", **kwargs):
    c = kwargs.get('context', context)
    with open(path, 'w') as f:
        f.write(render(c))

if __name__ == '__main__':
    pass
