import os
from django.template import Template, Context

gunicorn_upstart="""description     "Starting {{DOMAINNAME}}"

start on startup
exec {{GUNICORN_START}}
respawn
"""
"""
    Render the webiste upstart command file to be placed in /etc/init/
    in order to start the site on boot up.
"""


init_context = {
    'GUNICORN_START':'',    # The abspath to the gunicorn_start script
    'DOMAINNAME':'',        # The domain name
}


def build_init(context=init_context):
    t = Template( gunicorn_upstart )
    c = Context( context )
    return t.render(c)
