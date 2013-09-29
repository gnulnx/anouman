#!/usr/bin/env python
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put in a few files to make sure it was called...
try: settings.configure()
except: pass

context = {
    'DOMAINNAME':'',
}

commands = """
#This section defines commands specified by Anouman

NGINX=/etc/init.d/nginx
DOMAINNAME={{DOMAINNAME}}

function site {
        if [ $1 == 'status' ];
        then
                sudo $NGINX status
                sudo status $DOMAINNAME
        fi

        if [ $1 == 'stop' ];
        then
                sudo $NGINX stop
                sudo stop $DOMAINNAME
        fi

        if [ $1 == 'start' ];
        then
                sudo $NGINX start
                sudo start $DOMAINNAME
        fi

        if [ $1 == 'reload' ];
        then
                sudo nginx -s reload
        fi
}"""



def render(context=context):
    t = Template( commands )
    c = Context( context )
    return t.render(c)



