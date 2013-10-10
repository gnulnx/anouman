#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put in a few files to make sure it was called...
try: settings.configure()
except: pass

class BaseTemplate:
    """ 
        This is the base class for template rendering
        Each template to render should extend from this class and 
        override minimall teh context, and template properties.
    """
   
    # This should describe the temptes context
    context = {
        'template':''   # This is the path to the template
    }

    @classmethod
    def render(cls, c={}):
        """
            Pass in a context our the defaults above will be used
        """
        cls.context.update(c)

        t = Template( open(cls.context['template']).read() )
        c = Context( cls.context )
        return t.render( c )

    @classmethod
    def save(cls, path, **kwargs):
        """
            path is the path to where the file will be saved
        """
        c = kwargs.get('context', cls.context)
        with open(path, 'w') as f:
            f.write(cls.render(c) )

class VagrantTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/Vagrantfile",
        'NAME':'site1',
        'PRIVATE':'192.168.100.100', #To use private network set to ip:  192.168.100.100
    } 

class GunicornTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/gunicorn_start.sh",
        'NAME':'website',                           # Name of the application
        'DJANGODIR':'./',                           # Django project director
        'USER':'username',                          # user to run as
        'GROUP':'username',                         # group to run as
        'NUM_WORKERS':3,                            # Number of Gunicorn threads.  2(proc)+1
        'VIRTUALENVDIR':'./virtualenv',             # Directory containing your projects virtual env
        'DJANGO_SETTINGS_MODULE':'website.settings',# the django settings file
        'DJANGO_WSGI_MODULE':'website.wsgi',        # your project wsgi module
        'GUNICORN':'virtualenv/bin/gunicorn',       # location of gunicorn.py
        'ERROR_LOG':'/var/log/gunicorn-error.log',        # recommend setting this to domain/logs/gunicorn-error.log
        'ACCESS_LOG':'/var/log/gunicorn-access.log',        # recommend setting this to domain/logs/gunicorn-error.log
        #   You can bind your server to a unix socket or to a port
        #   But you should only bind it to one or the other
        #   unix socket example: /var/run/gunicorn.sock
        #   ip:port example:    10.0.2.13:8000
        'BIND':False,                      # ex:  10.0.2.13:80
        'SOCKFILE':False,                   # ex:  /var/run/gunicorn.sock
    }

class NginxTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/nginx.conf",
        'UNIXBIND':'',
        'DOMAINNAME':'',
        'DJANGO_STATIC':'',
        'DJANGO_MEDIA':'',
        'ACCESS_LOG':'',    # Project/Site based logs
        'ERROR_LOG':''      # Project/Site based logs
    }

class VagrantBootstrapTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/vagrant_bootstrap.sh",
        'NGINX':True,
        'MYSQL':False,
    }

class UpstateTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/upstart.conf",
        'GUNICORN_START':'',    # The abspath to the gunicorn_start script
        'DOMAINNAME':'',        # The domain name
    }    


class ShellCommandTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/shell_commands",
        'DOMAINNAME':'',
    }

    @classmethod
    def save(cls, path="./site.conf", **kwargs):
        """
            Overridden because we need to append and not write to the activate file
        """
        c = kwargs.get('context', cls.context)
        with open(path, 'a') as f:
            f.write(cls.render(c) ) 


class CleanTemplate(BaseTemplate):
    context = {
        'template':os.path.dirname(os.path.realpath(__file__)) + "/clean.sh",
        'DOMAINNAME':'site1.com',
    }
