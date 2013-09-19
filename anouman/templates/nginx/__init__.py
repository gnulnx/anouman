import os
from django.template import Template, Context
from django.conf import settings
settings.configure()

"""
    Build the nginx upstart command that will run the site
"""


nginx_context = {
    'UNIXBIND':'',
    'DOMAINNAME':'',
    'DJANGO_STATIC':'',
    'DJANGO_MEDIA':'',

    #   You can bind your server to a unix socket or to a port
    #   But you should only bind it to one or the other
    'BIND':False,                      # ex:  10.0.2.13:80
    'SOCKFILE':False,                   # ex:  /var/run/gunicorn.sock
}


template_dir = os.path.dirname(__file__)
def nginx_upstart(context=nginx_context):
    with open('%s/ngix_site.template'%(template_dir), 'r') as f:
        t = Template( f.read() )
        c = Context( context )
        return t.render(c)
