import os
from django.template import Template, Context
#from django.conf import settings
#settings.configure()

"""
    Render the webiste upstart command file to be placed in /etc/init/
    in order to start the site on boot up.
"""


init_context = {
    'GUNICORN_START':'',    # The abspath to the gunicorn_start script
    'DOMAINNAME':'',        # The domain name
}


template_dir = os.path.dirname(__file__)
def build_init(context=init_context):
    with open('%s/website.conf'%(template_dir), 'r') as f:
        t = Template( f.read() )
        c = Context( context )
        return t.render(c)
