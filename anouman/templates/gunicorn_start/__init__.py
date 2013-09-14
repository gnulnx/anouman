import os
from django.template import Template, Context
from django.conf import settings
settings.configure()

"""
    Render the gunicorn_start.py command file.

    gunicorn_start.py is a custom configued gunicorn script
    based on your django projec.

    
"""


gunicorn_context = {
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
    'BIND':False,                      # ex:  10.0.2.13:80
    'SOCKFILE':False,                   # ex:  /var/run/gunicorn.sock
}


template_dir = os.path.dirname(__file__)
def gunicorn_start(context=gunicorn_context):
    with open('%s/gunicorn_start.template'%(template_dir), 'r') as f:
        t = Template( f.read() )
        c = Context( context )
        return t.render(c)
