#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

settings.configure()

class BaseTemplate:
    """ 
        This is the base class for template rendering
        Each template to render should extend from this class and 
        override minimalliy the context and template properties.
    """

    # absolute path to the template file
    template = ''   

    # The context that will be passed to the template
    # Sublcasses should specify their own context parameters
    context = {}

    @classmethod
    def render(cls, c={}):
        """
            Pass in a context our the defaults above will be used
        """
        cls.context.update(c)
        t = Template( open(cls.template).read() )
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
    template = os.path.dirname(os.path.realpath(__file__)) + "/Vagrantfile"
    context = {
        'NAME':'site1',
        'PRIVATE':'192.168.100.100', #To use private network set to ip:  192.168.100.100
    } 

class GunicornTemplate(BaseTemplate):
    template=os.path.dirname(os.path.realpath(__file__)) + "/gunicorn_start.sh"

    context = {
        'NAME':'website',                               # Name of the application
        'DJANGODIR':'./',                               # Django project director
        'USER':'username',                              # user to run as
        'GROUP':'username',                             # group to run as
        'NUM_WORKERS':3,                                # Number of Gunicorn threads.  2(proc)+1
        'VIRTUALENVDIR':'./virtualenv',                 # Directory containing your projects virtual env
        'DJANGO_SETTINGS_MODULE':'website.settings',    # the django settings file
        'DJANGO_WSGI_MODULE':'website.wsgi',            # your project wsgi module
        'GUNICORN':'virtualenv/bin/gunicorn',           # location of gunicorn.py
        'ERROR_LOG':'/var/log/gunicorn-error.log',      # recommend setting this to domain/logs/gunicorn-error.log
        'ACCESS_LOG':'/var/log/gunicorn-access.log',    # recommend setting this to domain/logs/gunicorn-error.log
        'SOCKFILE':False,                               # ex:  /var/run/gunicorn.sock 
        #   You can bind your server to a unix socket or to a port
        #   But you should only bind it to one or the other
        #   unix socket example: /var/run/gunicorn.sock
        #   ip:port example:    10.0.2.13:8000
        'BIND':False,                                   # ex:  10.0.2.13:80  Use
    }

class NginxTemplate(BaseTemplate):
    template=os.path.dirname(os.path.realpath(__file__)) + "/nginx.conf"
    context = {
        'UNIXBIND':'',
        'DOMAINNAME':'',
        'DJANGO_STATIC':'',
        'DJANGO_MEDIA':'',
        'ACCESS_LOG':'',    # Project/Site based logs
        'ERROR_LOG':''      # Project/Site based logs
    }

class VagrantBootstrapTemplate(BaseTemplate):
    template=os.path.dirname(os.path.realpath(__file__)) + "/vagrant_bootstrap.sh"

    context = {
        'NGINX':True,
        'MYSQL':False,
    }

class UpstateTemplate(BaseTemplate):
    template=os.path.dirname(os.path.realpath(__file__)) + "/upstart.conf"

    context = {
        'GUNICORN_START':'',    # The abspath to the gunicorn_start script
        'DOMAINNAME':'',        # The domain name
    }    


class ShellCommandTemplate(BaseTemplate):
    template=os.path.dirname(os.path.realpath(__file__)) + "/shell_commands"

    context = {
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
    template=os.path.dirname(os.path.realpath(__file__)) + "/clean.sh"

    context = {
        'DOMAINNAME':'site1.com',
    }

