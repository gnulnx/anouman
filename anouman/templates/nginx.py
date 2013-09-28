#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put in a few files to make sure it was called...
try: setting
except: pass


"""
    Build the nginx upstart command that will run the site
"""

# The context variables which can be modified
context = {
    'UNIXBIND':'',
    'DOMAINNAME':'',
    'DJANGO_STATIC':'',
    'DJANGO_MEDIA':'',
}

# The nginx template.
nginx_site_conf="""upstream {{DOMAINNAME}} {
  # bind to the upstream unix socket and continue to retry even if it failed
  # to return a good HTTP response
  server {{UNIXBIND}} fail_timeout=0;
}
 
server {
 
    listen   80;
    server_name {{DOMAINNAME}}  www.{{DOMAINNAME}};
 
    client_max_body_size 128M;
 
    #access_log /webapps/hello_django/logs/nginx-access.log;
    #error_log /webapps/hello_django/logs/nginx-error.log;

    access_log  {{ACCESS_LOG}};
    error_log   {{ERROR_LOG}};
 
    location /static/ {
        alias   {{DJANGO_STATIC}};
    }
    
    location /media/ {
        alias   {{DJANGO_MEDIA}};
    }
 
    location / {
        # set the HTTP header
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 
        # pass the Host: header from the client right along so redirects
        # can be set correctly in the Django application
        proxy_set_header Host $http_host;
 
        # we don't want nginx trying to do something clever with
        # redirects, we set the Host: header above already.
        proxy_redirect off;
 
        # Let nginx server teh static files while gunicorn focuses on the python/db content
        if (!-f $request_filename) {
            proxy_pass http://{{DOMAINNAME}};
            break;
        }
    }
 
    # Error pages
    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root {{DJANGO_STATIC}};
    }
}
"""

def render(c={}):
    context.update(c)
    t = Template( nginx_site_conf )
    c = Context( context )
    return t.render(c)

def save(path="./site.conf", **kwargs):
    c = kwargs.get('context', context)
    with open(path, 'w') as f:
        f.write(render(c) )
    
