import os
from django.template import Template, Context

context = {
    'GUNICORN_START':'',    # The abspath to the gunicorn_start script
    'DOMAINNAME':'',        # The domain name
}

gunicorn_upstart="""description     "Starting {{DOMAINNAME}}"

start on startup
exec {{GUNICORN_START}}
respawn
"""
"""
    Render the webiste upstart command file to be placed in /etc/init/
    in order to start the site on boot up.
"""




def render(c={}):
    context.update(c)
    t = Template( gunicorn_upstart )
    c = Context( context )
    return t.render(c)

def save(path="", **kwargs):
    c = kwargs.get('context', context)
    with open(path, 'w') as f:
        f.write(render(c) )
