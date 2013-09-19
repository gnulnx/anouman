import os
from django.template import Template, Context

"""
    Build the nginx upstart command that will run the site
"""


nginx_context = {
    'UNIXBIND':'',
    'DOMAINNAME':'',
    'DJANGO_STATIC':'',
    'DJANGO_MEDIA':'',
}


template_dir = os.path.dirname(__file__)
def nginx_upstart(context=nginx_context):
    with open('%s/ngix_site.template'%(template_dir), 'r') as f:
        t = Template( f.read() )
        c = Context( context )
        return t.render(c)
